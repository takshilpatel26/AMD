import React, { useState, useEffect } from 'react'
import VillageLiveMap from './components/VillageLiveMap'

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1'

// Login Component
function AdminLogin({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/admin/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (data.success) {
        localStorage.setItem('admin_token', data.tokens.access)
        localStorage.setItem('admin_user', JSON.stringify(data.user))
        onLogin(data.user)
      } else {
        setError(data.error || 'Login failed')
      }
    } catch (err) {
      setError('Network error. Make sure backend is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '40px',
        width: '100%',
        maxWidth: '400px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ fontSize: '3rem', marginBottom: '10px' }}>🏛️</div>
          <h1 style={{ margin: '0 0 10px 0', color: '#333', fontSize: '1.8rem' }}>
            Admin Console
          </h1>
          <p style={{ margin: 0, color: '#666', fontSize: '0.95rem' }}>
            Village Grid Monitoring System
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: 600,
              color: '#444'
            }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: 600,
              color: '#444'
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          {error && (
            <div style={{
              background: '#fee',
              color: '#c00',
              padding: '12px',
              borderRadius: '8px',
              marginBottom: '20px',
              fontSize: '0.9rem'
            }}>
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              background: loading ? '#999' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onMouseOver={(e) => !loading && (e.target.style.transform = 'translateY(-2px)')}
            onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
          >
            {loading ? '⏳ Signing in...' : '🔐 Sign In'}
          </button>
        </form>

        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: '#f5f5f5',
          borderRadius: '8px',
          fontSize: '0.85rem',
          color: '#666'
        }}>
          <div style={{ fontWeight: 600, marginBottom: '8px' }}>Demo Credentials:</div>
          <div>Username: <code style={{ background: '#e8e8e8', padding: '2px 6px', borderRadius: '4px' }}>admin</code></div>
          <div>Password: <code style={{ background: '#e8e8e8', padding: '2px 6px', borderRadius: '4px' }}>admin123</code></div>
        </div>
      </div>
    </div>
  )
}

// Dashboard Component
function AdminDashboard({ user, onLogout }) {
  return (
    <div style={{height:'100vh', display:'flex', flexDirection:'column', background:'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}>
      <div style={{padding:'15px 20px', color:'white', display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <div>
          <h1 style={{margin:'0 0 5px 0', fontSize:'1.8rem'}}>🏘️ Village Grid Live Monitor</h1>
          <p style={{margin:'0', fontSize:'0.9rem', opacity:0.9}}>Real-time voltage and power monitoring across 500 houses</p>
        </div>
        <div style={{display:'flex', alignItems:'center', gap:'15px'}}>
          <span style={{fontSize:'0.9rem', opacity:0.9}}>
            👤 {user?.name || user?.username} ({user?.role})
          </span>
          <button 
            onClick={onLogout}
            style={{
              padding:'8px 16px',
              background:'rgba(255,255,255,0.2)',
              color:'white',
              border:'1px solid rgba(255,255,255,0.3)',
              borderRadius:'6px',
              cursor:'pointer',
              fontSize:'0.9rem'
            }}
          >
            Logout
          </button>
        </div>
      </div>
      
      <div style={{flex:1, margin:'0 20px 20px 20px', borderRadius:'12px', overflow:'hidden', boxShadow:'0 10px 30px rgba(0,0,0,0.3)'}}>
        <VillageLiveMap />
      </div>

      <div style={{padding:'15px 20px', display:'flex', justifyContent:'center', gap:'20px', flexWrap:'wrap', background:'rgba(255,255,255,0.9)', borderRadius:'12px', margin:'0 20px 20px 20px'}}>
        <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
          <div style={{width:'16px', height:'16px', borderRadius:'50%', background:'#00FF00', border:'2px solid white'}}></div>
          <span style={{fontSize:'0.9rem', fontWeight:600}}>Optimal (190-245V)</span>
        </div>
        <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
          <div style={{width:'16px', height:'16px', borderRadius:'50%', background:'#FFA500', border:'2px solid white'}}></div>
          <span style={{fontSize:'0.9rem', fontWeight:600}}>Brownout (&lt;190V)</span>
        </div>
        <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
          <div style={{width:'16px', height:'16px', borderRadius:'50%', background:'#FFFF00', border:'2px solid white'}}></div>
          <span style={{fontSize:'0.9rem', fontWeight:600}}>High (245-260V)</span>
        </div>
        <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
          <div style={{width:'16px', height:'16px', borderRadius:'50%', background:'#FF0000', border:'2px solid white'}}></div>
          <span style={{fontSize:'0.9rem', fontWeight:600}}>Surge (&gt;260V)</span>
        </div>
        <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
          <div style={{width:'16px', height:'16px', borderRadius:'50%', background:'#000000', border:'2px solid white'}}></div>
          <span style={{fontSize:'0.9rem', fontWeight:600}}>Outage (0V)</span>
        </div>
      </div>
    </div>
  )
}

// Main App
export default function App(){
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('admin_user')
    const token = localStorage.getItem('admin_token')
    
    if (storedUser && token) {
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
    setUser(null)
  }

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontSize: '1.2rem'
      }}>
        ⏳ Loading...
      </div>
    )
  }

  if (!user) {
    return <AdminLogin onLogin={handleLogin} />
  }

  return <AdminDashboard user={user} onLogout={handleLogout} />
}
