// AI Insights Component - ML-Powered Analytics Dashboard
import React, { useState, useEffect, useMemo } from 'react';
import { 
  Brain, 
  Sparkles, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  Zap,
  Activity,
  Target,
  Shield,
  Clock,
  ChevronRight,
  Lightbulb,
  Cpu,
  BarChart3,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react';

// ML Confidence Ring
const ConfidenceRing = ({ value, size = 60, color = '#10b981' }) => {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (value / 100) * circumference;
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth="4"
          fill="transparent"
          className="text-gray-200 dark:text-gray-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth="4"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-bold" style={{ color }}>{value}%</span>
      </div>
    </div>
  );
};

// Animated Pulse Dot
const PulseDot = ({ color = 'green', size = 'sm' }) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };
  
  const colorClasses = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    blue: 'bg-blue-500'
  };
  
  return (
    <span className="relative flex">
      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${colorClasses[color]} opacity-75`}></span>
      <span className={`relative inline-flex rounded-full ${sizeClasses[size]} ${colorClasses[color]}`}></span>
    </span>
  );
};

// AI Status Badge
const AIStatusBadge = ({ status, label }) => {
  const config = {
    normal: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400', icon: CheckCircle2 },
    warning: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-400', icon: AlertCircle },
    critical: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', icon: XCircle },
    analyzing: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400', icon: RefreshCw },
  };
  
  const c = config[status] || config.normal;
  const Icon = c.icon;
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${c.bg} ${c.text}`}>
      <Icon className={`w-3.5 h-3.5 ${status === 'analyzing' ? 'animate-spin' : ''}`} />
      {label}
    </span>
  );
};

const AIInsights = ({ meterData, className = '' }) => {
  const [aiAnalysis, setAiAnalysis] = useState({
    healthScore: 0,
    anomalyScore: 0,
    efficiencyScore: 0,
    predictions: [],
    recommendations: [],
    anomalies: [],
    lastUpdated: null,
    isAnalyzing: true
  });

  // Simulate ML analysis with realistic patterns
  useEffect(() => {
    const analyzeData = () => {
      const voltage = meterData?.voltage || 230;
      const current = meterData?.current || 5;
      const power = meterData?.power || 1150;
      const powerFactor = meterData?.powerFactor || 0.92;
      
      // Calculate health score based on multiple factors
      const voltageScore = voltage >= 220 && voltage <= 240 ? 100 : 
                          voltage >= 210 && voltage <= 250 ? 80 : 60;
      const pfScore = powerFactor * 100;
      const loadScore = power < 3000 ? 95 : power < 5000 ? 80 : 65;
      const healthScore = Math.round((voltageScore * 0.4 + pfScore * 0.35 + loadScore * 0.25));
      
      // Anomaly detection with confidence
      const anomalyScore = voltage > 250 || voltage < 200 ? 85 : 
                          current > 15 ? 70 : 
                          powerFactor < 0.8 ? 60 : 15;
      
      // Efficiency analysis
      const efficiencyScore = Math.round(pfScore * 0.6 + loadScore * 0.4);
      
      // Generate predictions
      const predictions = [
        {
          id: 1,
          type: 'consumption',
          title: 'Next Month Forecast',
          value: `${(meterData?.energy || 234) * 1.08}`,
          unit: 'kWh',
          confidence: 87,
          trend: 'up',
          change: '+8%',
          description: 'Based on seasonal patterns and historical data'
        },
        {
          id: 2,
          type: 'cost',
          title: 'Projected Bill',
          value: `₹${Math.round((meterData?.energy || 234) * 5.8)}`,
          unit: '',
          confidence: 91,
          trend: 'up',
          change: '+5%',
          description: 'Including predicted rate adjustments'
        },
        {
          id: 3,
          type: 'peak',
          title: 'Peak Load Time',
          value: '10:30 AM',
          unit: '',
          confidence: 94,
          trend: 'neutral',
          change: 'Today',
          description: 'Optimal time to reduce heavy equipment usage'
        }
      ];
      
      // Generate smart recommendations
      const recommendations = [
        {
          id: 1,
          priority: 'high',
          icon: Zap,
          title: 'Shift irrigation to off-peak hours',
          description: 'Save ₹350/month by running pumps between 10 PM - 6 AM',
          savings: '₹350/mo',
          confidence: 89,
          action: 'Schedule Now'
        },
        {
          id: 2,
          priority: 'medium',
          icon: Target,
          title: 'Power factor improvement needed',
          description: `Current PF: ${(powerFactor * 100).toFixed(0)}%. Install capacitor bank for better efficiency`,
          savings: '₹200/mo',
          confidence: 82,
          action: 'Learn More'
        },
        {
          id: 3,
          priority: 'low',
          icon: Lightbulb,
          title: 'Consider solar integration',
          description: 'Your consumption pattern is ideal for solar. ROI in 4.2 years',
          savings: '₹1,500/mo',
          confidence: 76,
          action: 'Get Quote'
        }
      ];
      
      // Detect anomalies
      const anomalies = [];
      if (voltage > 250) {
        anomalies.push({
          id: 1,
          type: 'critical',
          title: 'High Voltage Detected',
          value: `${voltage}V`,
          threshold: '250V',
          confidence: 95,
          timestamp: new Date(),
          recommendation: 'Contact utility provider immediately'
        });
      }
      if (voltage < 200) {
        anomalies.push({
          id: 2,
          type: 'warning',
          title: 'Low Voltage Alert',
          value: `${voltage}V`,
          threshold: '200V',
          confidence: 92,
          timestamp: new Date(),
          recommendation: 'Check for grid issues in your area'
        });
      }
      if (powerFactor < 0.85) {
        anomalies.push({
          id: 3,
          type: 'warning',
          title: 'Poor Power Factor',
          value: `${(powerFactor * 100).toFixed(0)}%`,
          threshold: '85%',
          confidence: 88,
          timestamp: new Date(),
          recommendation: 'Install power factor correction capacitors'
        });
      }
      
      setAiAnalysis({
        healthScore,
        anomalyScore,
        efficiencyScore,
        predictions,
        recommendations,
        anomalies,
        lastUpdated: new Date(),
        isAnalyzing: false
      });
    };
    
    // Initial analysis
    setAiAnalysis(prev => ({ ...prev, isAnalyzing: true }));
    const timer = setTimeout(analyzeData, 1500);
    
    return () => clearTimeout(timer);
  }, [meterData]);

  const getHealthColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* AI Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl shadow-lg">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              AI Insights
              <Sparkles className="w-5 h-5 text-yellow-500" />
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              ML-powered analysis • Updated {aiAnalysis.lastUpdated ? 'just now' : 'analyzing...'}
            </p>
          </div>
        </div>
        <AIStatusBadge 
          status={aiAnalysis.isAnalyzing ? 'analyzing' : 
                 aiAnalysis.anomalies.length > 0 ? 'warning' : 'normal'} 
          label={aiAnalysis.isAnalyzing ? 'Analyzing' : 
                aiAnalysis.anomalies.length > 0 ? `${aiAnalysis.anomalies.length} Issues` : 'All Clear'}
        />
      </div>

      {/* Health Scores Grid */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">System Health</span>
            <Shield className="w-4 h-4 text-gray-400" />
          </div>
          <div className="flex items-center gap-3">
            <ConfidenceRing 
              value={aiAnalysis.healthScore} 
              color={getHealthColor(aiAnalysis.healthScore)} 
            />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {aiAnalysis.healthScore}
              </p>
              <p className="text-xs text-gray-500">out of 100</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Anomaly Risk</span>
            <AlertTriangle className="w-4 h-4 text-gray-400" />
          </div>
          <div className="flex items-center gap-3">
            <ConfidenceRing 
              value={aiAnalysis.anomalyScore} 
              color={aiAnalysis.anomalyScore > 50 ? '#ef4444' : aiAnalysis.anomalyScore > 30 ? '#f59e0b' : '#10b981'} 
            />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {aiAnalysis.anomalyScore > 50 ? 'High' : aiAnalysis.anomalyScore > 30 ? 'Medium' : 'Low'}
              </p>
              <p className="text-xs text-gray-500">{aiAnalysis.anomalyScore}% risk level</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Efficiency</span>
            <Activity className="w-4 h-4 text-gray-400" />
          </div>
          <div className="flex items-center gap-3">
            <ConfidenceRing 
              value={aiAnalysis.efficiencyScore} 
              color={aiAnalysis.efficiencyScore >= 80 ? '#10b981' : '#3b82f6'} 
            />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {aiAnalysis.efficiencyScore}%
              </p>
              <p className="text-xs text-gray-500">optimal range</p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Anomalies */}
      {aiAnalysis.anomalies.length > 0 && (
        <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 dark:from-red-900/20 dark:to-orange-900/20 rounded-xl p-4 border border-red-200 dark:border-red-800">
          <div className="flex items-center gap-2 mb-3">
            <PulseDot color="red" size="md" />
            <h3 className="font-semibold text-red-700 dark:text-red-400">Active Anomalies Detected</h3>
          </div>
          <div className="space-y-3">
            {aiAnalysis.anomalies.map((anomaly) => (
              <div 
                key={anomaly.id} 
                className="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg p-3"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    anomaly.type === 'critical' ? 'bg-red-100 dark:bg-red-900/30' : 'bg-yellow-100 dark:bg-yellow-900/30'
                  }`}>
                    <AlertTriangle className={`w-4 h-4 ${
                      anomaly.type === 'critical' ? 'text-red-600' : 'text-yellow-600'
                    }`} />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{anomaly.title}</p>
                    <p className="text-sm text-gray-500">{anomaly.value} (threshold: {anomaly.threshold})</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-medium text-gray-500">{anomaly.confidence}% confidence</span>
                  <p className="text-xs text-blue-600 dark:text-blue-400 cursor-pointer hover:underline">
                    {anomaly.recommendation}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Predictions */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-violet-500" />
            ML Predictions
          </h3>
          <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
            Neural Network v2.1
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {aiAnalysis.predictions.map((pred) => (
            <div 
              key={pred.id}
              className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-100 dark:border-gray-700"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500">{pred.title}</span>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                  pred.trend === 'up' ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' :
                  pred.trend === 'down' ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' :
                  'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {pred.change}
                </span>
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {pred.value}{pred.unit}
              </p>
              <div className="flex items-center gap-2 mt-2">
                <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full transition-all duration-1000"
                    style={{ width: `${pred.confidence}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{pred.confidence}%</span>
              </div>
              <p className="text-xs text-gray-400 mt-2">{pred.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Smart Recommendations */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            Smart Recommendations
          </h3>
          <span className="text-xs text-emerald-600 font-medium">
            Potential savings: ₹2,050/mo
          </span>
        </div>
        <div className="space-y-3">
          {aiAnalysis.recommendations.map((rec) => (
            <div 
              key={rec.id}
              className={`p-4 rounded-lg border-l-4 ${
                rec.priority === 'high' ? 'border-red-500 bg-red-50 dark:bg-red-900/10' :
                rec.priority === 'medium' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/10' :
                'border-green-500 bg-green-50 dark:bg-green-900/10'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    rec.priority === 'high' ? 'bg-red-100 dark:bg-red-900/30' :
                    rec.priority === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30' :
                    'bg-green-100 dark:bg-green-900/30'
                  }`}>
                    <rec.icon className={`w-4 h-4 ${
                      rec.priority === 'high' ? 'text-red-600' :
                      rec.priority === 'medium' ? 'text-yellow-600' :
                      'text-green-600'
                    }`} />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{rec.title}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{rec.description}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-sm font-semibold text-emerald-600">Save {rec.savings}</span>
                      <span className="text-xs text-gray-400">• {rec.confidence}% confidence</span>
                    </div>
                  </div>
                </div>
                <button className="px-3 py-1.5 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg text-sm font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors flex items-center gap-1">
                  {rec.action}
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AIInsights;
