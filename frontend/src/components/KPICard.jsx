// Reusable KPI Card Component
import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const KPICard = ({ 
  title, 
  value, 
  unit, 
  icon: Icon, 
  trend, 
  trendValue,
  subtitle,
  iconBg = 'bg-emerald-100',
  iconColor = 'text-emerald-600',
  valueColor = 'text-slate-900',
  className = '',
  badge,
  glowEffect = false,
}) => {
  return (
    <div className={`relative overflow-hidden bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm p-6 rounded-2xl shadow-glass border border-slate-100 dark:border-slate-700 group hover:shadow-glass-lg hover:-translate-y-1 transition-all duration-300 ${glowEffect ? 'animate-glow' : ''} ${className}`}>
      {/* Background Icon */}
      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
        <Icon size={80} className={iconColor} />
      </div>

      {/* Content */}
      <div className="flex justify-between items-start relative z-10">
        <div className="flex-1">
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider">
            {title}
          </p>
          
          <div className="flex items-baseline gap-2 mt-2">
            <h3 className={`text-4xl font-extrabold ${valueColor} dark:text-slate-100`}>
              {value}
            </h3>
            {unit && (
              <span className="text-lg text-slate-400 dark:text-slate-500 font-normal">{unit}</span>
            )}
          </div>

          {/* Trend or Subtitle */}
          {trend && (
            <div className={`mt-4 flex items-center gap-2 text-sm font-medium ${
              trend === 'up' ? 'text-emerald-600 dark:text-emerald-400' : 
              trend === 'down' ? 'text-red-600 dark:text-red-400' : 
              'text-slate-600 dark:text-slate-400'
            }`}>
              {trend === 'up' && <ArrowUpRight size={16} />}
              {trend === 'down' && <ArrowDownRight size={16} />}
              <span>{trendValue}</span>
            </div>
          )}

          {subtitle && (
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-4">{subtitle}</p>
          )}
        </div>

        {/* Icon or Badge */}
        <div className="flex flex-col items-end gap-2">
          {Icon && (
            <div className={`p-3 ${iconBg} dark:bg-opacity-20 rounded-xl ${iconColor} dark:text-emerald-400 ${glowEffect ? 'animate-pulse' : ''}`}>
              <Icon size={24} />
            </div>
          )}
          
          {badge && (
            <div className="px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-xs font-bold text-slate-700 dark:text-slate-300">
              {badge}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KPICard;
