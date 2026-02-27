// Efficiency Grade Badge Component
import React from 'react';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import { getEfficiencyColor } from '../utils/helpers';

const EfficiencyBadge = ({ score, grade, size = 'large', showLabel = true }) => {
  const color = getEfficiencyColor(score);
  
  const sizeClasses = {
    small: 'h-8 w-8 text-xs',
    medium: 'h-10 w-10 text-sm',
    large: 'h-12 w-12 text-base',
  };

  const bgColors = {
    emerald: 'bg-emerald-100 dark:bg-emerald-900/50 border-emerald-500 dark:border-emerald-400 text-emerald-800 dark:text-emerald-200',
    blue: 'bg-blue-100 dark:bg-blue-900/50 border-blue-500 dark:border-blue-400 text-blue-800 dark:text-blue-200',
    amber: 'bg-amber-100 dark:bg-amber-900/50 border-amber-500 dark:border-amber-400 text-amber-800 dark:text-amber-200',
    red: 'bg-red-100 dark:bg-red-900/50 border-red-500 dark:border-red-400 text-red-800 dark:text-red-200',
  };

  const textColors = {
    emerald: 'text-emerald-600 dark:text-emerald-400',
    blue: 'text-blue-600 dark:text-blue-400',
    amber: 'text-amber-600 dark:text-amber-400',
    red: 'text-red-600 dark:text-red-400',
  };

  const Icon = score >= 80 ? CheckCircle2 : AlertCircle;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`${sizeClasses[size]} rounded-full ${bgColors[color]} border-4 flex items-center justify-center font-bold shadow-lg`}>
        {grade}
      </div>
      
      {showLabel && (
        <div className={`flex items-center gap-1 text-sm ${textColors[color]}`}>
          <Icon size={14} />
          <span className="font-medium">
            {score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : score >= 40 ? 'Average' : 'Poor'}
          </span>
        </div>
      )}
    </div>
  );
};

export default EfficiencyBadge;
