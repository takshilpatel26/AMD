// Loading Spinner Component
import React from 'react';
import { Zap } from 'lucide-react';

const LoadingSpinner = ({ size = 'medium', text }) => {
  const sizes = {
    small: 'h-8 w-8',
    medium: 'h-12 w-12',
    large: 'h-16 w-16',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8">
      <div className="relative">
        <div className={`${sizes[size]} border-4 border-emerald-200 dark:border-emerald-700 border-t-emerald-500 dark:border-t-emerald-400 rounded-full animate-spin`}></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Zap size={size === 'large' ? 24 : size === 'medium' ? 16 : 12} className="text-emerald-500 dark:text-emerald-400 animate-pulse" />
        </div>
      </div>
      {text && (
        <p className="text-slate-600 dark:text-slate-300 text-sm font-medium animate-pulse">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
