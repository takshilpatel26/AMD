// Alert Card Component
import React from 'react';
import { AlertTriangle, Zap, Info, AlertCircle, CheckCircle2 } from 'lucide-react';
import { getAlertStyle } from '../utils/helpers';
import { formatDateTime } from '../utils/helpers';

const AlertCard = ({ 
  alert, 
  onAcknowledge,
  compact = false,
}) => {
  const style = getAlertStyle(alert.severity);
  
  const icons = {
    voltage_spike: AlertTriangle,
    high_usage: Zap,
    peak_hours: Info,
    anomaly: AlertCircle,
    default: AlertTriangle,
  };

  const Icon = icons[alert.type] || icons.default;

  if (compact) {
    return (
      <div className={`p-3 ${style.bg} border-l-4 ${style.border} rounded-r-xl transition-all hover:shadow-md`}>
        <div className={`flex items-center gap-2 ${style.text} font-bold text-sm`}>
          <Icon size={16} className={`${style.icon} ${alert.severity === 'critical' ? 'animate-pulse' : ''}`} />
          {alert.message}
        </div>
        {alert.details && (
          <p className={`text-xs ${style.text} opacity-80 mt-1 pl-6`}>
            {alert.details}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={`p-4 ${style.bg} border-l-4 ${style.border} rounded-r-2xl transition-all hover:shadow-lg`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1">
          <div className={`p-2 bg-white/50 rounded-lg ${style.icon} ${alert.severity === 'critical' ? 'animate-pulse' : ''}`}>
            <Icon size={20} />
          </div>
          
          <div className="flex-1">
            <h4 className={`font-bold text-sm ${style.text}`}>
              {alert.message}
            </h4>
            {alert.details && (
              <p className={`text-xs ${style.text} opacity-80 mt-1`}>
                {alert.details}
              </p>
            )}
            {alert.timestamp && (
              <p className={`text-xs ${style.text} opacity-60 mt-2`}>
                {formatDateTime(alert.timestamp)}
              </p>
            )}
          </div>
        </div>

        {!alert.acknowledged && onAcknowledge && (
          <button
            onClick={() => onAcknowledge(alert.id)}
            className={`px-3 py-1 bg-white/80 hover:bg-white rounded-lg text-xs font-medium ${style.text} transition-all flex items-center gap-1 shadow-sm hover:shadow`}
          >
            <CheckCircle2 size={14} />
            <span>Ack</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default AlertCard;
