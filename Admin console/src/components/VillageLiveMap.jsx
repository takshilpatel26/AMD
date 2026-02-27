import React, { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import L from 'leaflet'

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1'

// Helper: deterministic pseudo-random from string
function seededRandom(str){
  let h = 2166136261 >>> 0
  for(let i=0;i<str.length;i++){
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 16777619) >>> 0
  }
  return (h >>> 0) / 4294967295
}

function generateCoordinates(houses){
  // Organic placement: uniform-in-circle around center using radial coords
  const centerLat = 28.4595
  const centerLng = 77.0266
  const radiusDeg = 0.0175 // ~2km radius; avoids square boundary

  return houses.map((h, i)=>{
    const id = (h.house_id || String(i)) + ''
    const rRand = seededRandom(id + '_r_' + i)
    const aRand = seededRandom(id + '_a_' + (i * 7919))
    const r = Math.sqrt(rRand) * radiusDeg
    const a = 2 * Math.PI * aRand
    const lat = centerLat + r * Math.sin(a)
    const lng = centerLng + r * Math.cos(a)
    return { ...h, lat, lng }
  })
}

const getVoltageColor = (v) => {
  if (v === 0) return '#000000'        // Black: Outage (0V)
  if (v > 260) return '#FF0000'        // Red: Surge (>260V)
  if (v >= 245 && v <= 260) return '#FFFF00'  // Yellow: High (245-260V)
  if (v < 190) return '#FFA500'        // Orange: Brownout (<190V)
  return '#00FF00'                     // Green: Optimal (190-245V)
}

function getStatusNote(voltage){
  if (voltage === 0) return '🚨 Outage'
  if (voltage > 260) return '⚡ Surge'
  if (voltage >= 245) return '⚠️ High'
  if (voltage < 190) return '📉 Brownout'
  return '✅ Optimal'
}

export default function VillageLiveMap(){
  const [houseStates, setHouseStates] = useState([])
  const [connectionStatus, setConnectionStatus] = useState('connecting')
  const [summary, setSummary] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [error, setError] = useState(null)
  
  // Fetch data from Django API
  const fetchVillageData = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const headers = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await fetch(`${API_BASE_URL}/admin/villagedata/`, {
        method: 'GET',
        headers,
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.success && data.houses) {
        const mapped = generateCoordinates(data.houses)
        setHouseStates(mapped)
        setSummary(data.summary)
        setLastUpdate(data.timestamp)
        setConnectionStatus('connected')
        setError(null)
      }
    } catch (err) {
      console.error('Failed to fetch village data:', err)
      setError(err.message)
      setConnectionStatus('error')
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchVillageData()
    
    // Poll every 3 seconds for updates
    const interval = setInterval(fetchVillageData, 3000)
    
    return () => clearInterval(interval)
  }, [])

  // If no live data yet, render demo data with random placement
  const display = houseStates.length ? houseStates : Array.from({length:500}).map((_,i)=>{
    const centerLat = 28.4595
    const centerLng = 77.0266
    const radiusDeg = 0.0175
    const id = 'demo-'+i
    const rRand = seededRandom(id + '_r_' + i)
    const aRand = seededRandom(id + '_a_' + (i * 7919))
    const r = Math.sqrt(rRand) * radiusDeg
    const a = 2 * Math.PI * aRand
    const lat = centerLat + r * Math.sin(a)
    const lng = centerLng + r * Math.cos(a)
    const v = [0, 230, 250, 265, 180][i % 5]
    return {
      house_id: id,
      name: 'House '+(i+1),
      voltage: v === 230 ? 230 + (Math.random()-0.5)*20 : v,
      usage_kw: +(Math.random()*8).toFixed(2),
      status_note: getStatusNote(v),
      lat,
      lng
    }
  })

  return (
    <div style={{width:'100%', height:'100%', position:'relative'}}>
      {/* Connection Status Badge */}
      <div style={{position:'absolute', top:'10px', right:'10px', zIndex:1000, background:'white', padding:'10px 15px', borderRadius:'20px', fontSize:'0.9rem', fontWeight:600, pointerEvents:'none', boxShadow:'0 4px 12px rgba(0,0,0,0.15)'}}>
        {connectionStatus === 'connected' ? <span style={{color:'#00c851'}}>🟢 Connected to API</span> : 
         connectionStatus === 'connecting' ? <span style={{color:'#ffaa00'}}>🟡 Connecting...</span> : 
         <span style={{color:'#ff4444'}}>🔴 Disconnected {error && `(${error})`}</span>}
      </div>
      
      {/* Summary Stats Panel */}
      {summary && (
        <div style={{
          position:'absolute', 
          top:'10px', 
          left:'10px', 
          zIndex:1000, 
          background:'rgba(255,255,255,0.95)', 
          padding:'15px 20px', 
          borderRadius:'12px', 
          fontSize:'0.85rem', 
          boxShadow:'0 4px 12px rgba(0,0,0,0.15)',
          maxWidth: '280px'
        }}>
          <div style={{fontWeight:700, marginBottom:'10px', fontSize:'1rem'}}>📊 Grid Summary</div>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'8px'}}>
            <div>🏠 Total: <b>{summary.total_houses}</b></div>
            <div>⚡ Avg V: <b>{summary.avg_voltage}V</b></div>
            <div style={{color:'#00c851'}}>✅ Normal: <b>{summary.normal}</b></div>
            <div style={{color:'#FFA500'}}>📉 Brownout: <b>{summary.brownout}</b></div>
            <div style={{color:'#FFD700'}}>⚠️ High V: <b>{summary.high_voltage}</b></div>
            <div style={{color:'#FF0000'}}>⚡ Surge: <b>{summary.surge}</b></div>
            <div style={{color:'#333'}}>🔌 Power: <b>{summary.total_power_kw.toFixed(1)} kW</b></div>
            {summary.outage > 0 && <div style={{color:'#000'}}>🚨 Outage: <b>{summary.outage}</b></div>}
          </div>
          {lastUpdate && (
            <div style={{marginTop:'10px', fontSize:'0.75rem', opacity:0.6}}>
              Updated: {new Date(lastUpdate).toLocaleTimeString()}
            </div>
          )}
        </div>
      )}
      
      <MapContainer center={[28.4595,77.0266]} zoom={14} style={{height:'100%', width:'100%'}} scrollWheelZoom={true} zoomControl={true} dragging={true} doubleClickZoom={true}>
        <TileLayer url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png" attribution='© OpenStreetMap contributors © CARTO' />

        {display.map(h => (
          <CircleMarker
            key={h.house_id}
            center={[h.lat, h.lng]}
            radius={6}
            pathOptions={{ 
              fillColor: getVoltageColor(h.voltage), 
              color: '#fff', 
              weight: 1.5, 
              fillOpacity: 0.85 
            }}
          >
            <Popup maxWidth={440} minWidth={320} className="house-popup">
              <div style={{fontSize:'14px', minWidth:'380px', lineHeight:1.5}}>
                <div style={{fontWeight:700, marginBottom:'6px'}}>{h.name || 'House'}</div>
                <div style={{marginBottom:'4px'}}>
                  <span style={{opacity:0.7}}>House ID:</span> <b>{h.house_id}</b>
                </div>
                <div style={{marginBottom:'4px'}}>
                  <span style={{opacity:0.7}}>Current Voltage:</span> <b>{(Number(h.voltage)||0).toFixed(1)} V</b>
                </div>
                <div style={{marginBottom:'4px'}}>
                  <span style={{opacity:0.7}}>Current Power:</span> <b>{Number(h.usage_kw).toFixed(2)} kW</b>
                </div>
                <div style={{marginBottom:'4px'}}>
                  <span style={{opacity:0.7}}>Status:</span> <b>{h.status_note}</b>
                </div>
                {h.last_updated ? (
                  <div style={{opacity:0.6, marginTop:'6px'}}>Updated: {h.last_updated}</div>
                ) : null}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
