// Usage Chart Component with Glassmorphism
import React, { lazy, Suspense } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CHART_COLORS } from '../constants/config';

const UsageChart = ({ data, title, height = 300 }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
        <p>No data available</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {title && (
        <h3 className="font-bold text-xl mb-6 text-slate-800 dark:text-slate-100">{title}</h3>
      )}
      
      <div style={{ height: `${height}px` }} className="w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
              </linearGradient>
            </defs>
            
            <CartesianGrid 
              strokeDasharray="3 3" 
              vertical={false} 
              stroke={CHART_COLORS.grid}
              opacity={0.5}
            />
            
            <XAxis 
              dataKey="time" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: CHART_COLORS.text, fontSize: 12 }}
              dy={10}
            />
            
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: CHART_COLORS.text, fontSize: 12 }}
              dx={-10}
              label={{ 
                value: 'kW', 
                angle: -90, 
                position: 'insideLeft',
                style: { fill: CHART_COLORS.text, fontSize: 12 }
              }}
            />
            
            <Tooltip 
              contentStyle={{
                backgroundColor: '#1e293b',
                borderRadius: '12px',
                border: 'none',
                color: '#fff',
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.2)',
                padding: '12px',
              }}
              itemStyle={{ color: CHART_COLORS.secondary }}
              labelStyle={{ color: '#cbd5e1', marginBottom: '4px' }}
              cursor={{ stroke: CHART_COLORS.primary, strokeWidth: 2, strokeDasharray: '5 5' }}
            />
            
            <Area 
              type="monotone" 
              dataKey="usage" 
              stroke={CHART_COLORS.primary} 
              strokeWidth={3} 
              fillOpacity={1} 
              fill="url(#colorUsage)"
              animationDuration={1000}
              dot={false}
              activeDot={{ 
                r: 6, 
                fill: CHART_COLORS.primary,
                stroke: '#fff',
                strokeWidth: 2,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default UsageChart;
