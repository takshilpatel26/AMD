// Features Page - Showcasing All USP Features for Hackathon
import React, { useState } from 'react';
import {
  Brain,
  Zap,
  Shield,
  Trophy,
  Users,
  Volume2,
  Languages,
  Wifi,
  WifiOff,
  Smartphone,
  Bell,
  TrendingUp,
  Leaf,
  Target,
  Award,
  Sparkles,
  ChevronRight,
  Play,
  CheckCircle2,
  Star
} from 'lucide-react';
import Navbar from '../components/Navbar';
import AIInsights from '../components/AIInsights';
import Gamification from '../components/Gamification';
import { AccessibilityPanel, VoiceAlertButton } from '../components/AccessibilityFeatures';

const FeatureCard = ({ icon: Icon, title, description, category, color, children }) => (
  <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
    <div className="flex items-start gap-4">
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div className="flex-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
          {category}
        </span>
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mt-1">{title}</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{description}</p>
        {children}
      </div>
    </div>
  </div>
);

const CategoryBadge = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
      active
        ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-200 dark:shadow-emerald-900/30'
        : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700'
    }`}
  >
    <Icon className="w-4 h-4" />
    {label}
  </button>
);

const Features = ({ onLogout }) => {
  const [activeCategory, setActiveCategory] = useState('all');
  const [showAIDemo, setShowAIDemo] = useState(false);
  const [showGamification, setShowGamification] = useState(false);
  
  const categories = [
    { id: 'all', label: 'All Features', icon: Sparkles },
    { id: 'ai', label: 'Best AI', icon: Brain },
    { id: 'impact', label: 'Best Impact', icon: Users },
    { id: 'design', label: 'Best Design', icon: Star },
  ];
  
  const features = [
    // AI Features
    {
      id: 1,
      category: 'ai',
      icon: Brain,
      title: 'ML-Powered Anomaly Detection',
      description: 'Real-time detection of voltage spikes, power fluctuations, and unusual consumption patterns using machine learning algorithms.',
      color: 'bg-gradient-to-br from-violet-500 to-purple-600',
      badge: 'Best AI'
    },
    {
      id: 2,
      category: 'ai',
      icon: TrendingUp,
      title: 'Predictive Consumption Forecasting',
      description: 'Neural network-based prediction of future energy consumption with 90%+ accuracy, helping users plan their usage.',
      color: 'bg-gradient-to-br from-blue-500 to-indigo-600',
      badge: 'Best AI'
    },
    {
      id: 3,
      category: 'ai',
      icon: Sparkles,
      title: 'Smart Recommendations Engine',
      description: 'AI-generated personalized tips to reduce energy bills based on usage patterns, weather, and seasonal factors.',
      color: 'bg-gradient-to-br from-amber-500 to-orange-600',
      badge: 'Best AI'
    },
    {
      id: 4,
      category: 'ai',
      icon: Shield,
      title: 'Predictive Maintenance Alerts',
      description: 'Early warning system for equipment failures using pattern recognition and historical data analysis.',
      color: 'bg-gradient-to-br from-red-500 to-pink-600',
      badge: 'Best AI'
    },
    
    // Impact Features
    {
      id: 5,
      category: 'impact',
      icon: Volume2,
      title: 'Multi-Language Voice Alerts',
      description: 'Voice notifications in English, Hindi, and Gujarati for illiterate rural farmers. Accessibility-first design.',
      color: 'bg-gradient-to-br from-emerald-500 to-teal-600',
      badge: 'Best Impact'
    },
    {
      id: 6,
      category: 'impact',
      icon: WifiOff,
      title: 'Offline-First Architecture',
      description: 'Full functionality without internet. Cached data, local storage, and sync when connected. Perfect for rural areas.',
      color: 'bg-gradient-to-br from-gray-500 to-slate-600',
      badge: 'Best Impact'
    },
    {
      id: 7,
      category: 'impact',
      icon: Smartphone,
      title: 'SMS-Based Alerts (No App Needed)',
      description: 'Critical alerts via SMS to basic phones. No smartphone or internet required. Reaches every farmer.',
      color: 'bg-gradient-to-br from-green-500 to-emerald-600',
      badge: 'Best Impact'
    },
    {
      id: 8,
      category: 'impact',
      icon: Leaf,
      title: 'Carbon Footprint Tracking',
      description: 'Environmental impact monitoring with CO2 savings calculator. Promoting sustainable energy practices.',
      color: 'bg-gradient-to-br from-lime-500 to-green-600',
      badge: 'Best Impact'
    },
    
    // Design Features
    {
      id: 9,
      category: 'design',
      icon: Trophy,
      title: 'Gamification & Achievements',
      description: 'Energy-saving badges, streaks, daily challenges, and community leaderboards. Making savings fun!',
      color: 'bg-gradient-to-br from-yellow-500 to-amber-600',
      badge: 'Best Design'
    },
    {
      id: 10,
      category: 'design',
      icon: Zap,
      title: 'Real-Time Data Visualization',
      description: 'Live updating charts, animated meters, and smooth transitions. Glass-morphism UI with dark mode.',
      color: 'bg-gradient-to-br from-cyan-500 to-blue-600',
      badge: 'Best Design'
    },
    {
      id: 11,
      category: 'design',
      icon: Target,
      title: 'Intuitive Dashboard',
      description: 'Clean, scannable interface with KPI cards, efficiency badges, and contextual information.',
      color: 'bg-gradient-to-br from-rose-500 to-pink-600',
      badge: 'Best Design'
    },
    {
      id: 12,
      category: 'design',
      icon: Bell,
      title: 'Smart Notification System',
      description: 'Priority-based alerts with customizable thresholds. Critical, warning, and info categories.',
      color: 'bg-gradient-to-br from-fuchsia-500 to-purple-600',
      badge: 'Best Design'
    },
  ];
  
  const filteredFeatures = activeCategory === 'all' 
    ? features 
    : features.filter(f => f.category === activeCategory);
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-mint-50/50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      <Navbar onLogout={onLogout} />
      
      <div className="p-4 md:p-6 max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <div className="text-center py-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-full text-emerald-700 dark:text-emerald-400 text-sm font-medium mb-4">
            <Award className="w-4 h-4" />
            Hackathon Showcase
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">
            Gram Meter <span className="text-emerald-500">Features</span>
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mt-4 max-w-2xl mx-auto">
            Smart energy monitoring for rural India. AI-powered insights, offline-first design, 
            and accessibility features that make a real impact.
          </p>
          
          {/* Category Stats */}
          <div className="flex justify-center gap-8 mt-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-violet-600 dark:text-violet-400">4</div>
              <div className="text-sm text-gray-500">AI Features</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">4</div>
              <div className="text-sm text-gray-500">Impact Features</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-amber-600 dark:text-amber-400">4</div>
              <div className="text-sm text-gray-500">Design Features</div>
            </div>
          </div>
        </div>
        
        {/* Category Filter */}
        <div className="flex flex-wrap gap-3 justify-center">
          {categories.map((cat) => (
            <CategoryBadge
              key={cat.id}
              icon={cat.icon}
              label={cat.label}
              active={activeCategory === cat.id}
              onClick={() => setActiveCategory(cat.id)}
            />
          ))}
        </div>
        
        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFeatures.map((feature) => (
            <FeatureCard
              key={feature.id}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              category={feature.badge}
              color={feature.color}
            />
          ))}
        </div>
        
        {/* Interactive Demos Section */}
        <div className="space-y-6 mt-12">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white text-center">
            Interactive Demos
          </h2>
          
          {/* AI Insights Demo */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            <button
              onClick={() => setShowAIDemo(!showAIDemo)}
              className="w-full p-6 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white">AI Insights Demo</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">See ML-powered anomaly detection in action</p>
                </div>
              </div>
              <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${showAIDemo ? 'rotate-90' : ''}`} />
            </button>
            
            {showAIDemo && (
              <div className="p-6 pt-0 border-t border-gray-100 dark:border-gray-700">
                <AIInsights meterData={{
                  voltage: 235,
                  current: 4.8,
                  power: 1128,
                  energy: 234,
                  powerFactor: 0.92
                }} />
              </div>
            )}
          </div>
          
          {/* Gamification Demo */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            <button
              onClick={() => setShowGamification(!showGamification)}
              className="w-full p-6 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-yellow-500 to-amber-600 rounded-xl">
                  <Trophy className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white">Gamification Demo</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Achievements, streaks, and community leaderboard</p>
                </div>
              </div>
              <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${showGamification ? 'rotate-90' : ''}`} />
            </button>
            
            {showGamification && (
              <div className="p-6 pt-0 border-t border-gray-100 dark:border-gray-700">
                <Gamification />
              </div>
            )}
          </div>
          
          {/* Voice Alert Demo */}
          <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-2xl p-6 border border-emerald-200 dark:border-emerald-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl">
                  <Volume2 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white">Voice Alert Demo</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Click to hear multi-language voice alerts</p>
                </div>
              </div>
              <div className="flex gap-2">
                <VoiceAlertButton messageKey="welcome" language="en" className="!bg-white dark:!bg-gray-800" />
                <VoiceAlertButton messageKey="welcome" language="hi" className="!bg-white dark:!bg-gray-800" />
                <VoiceAlertButton messageKey="welcome" language="gu" className="!bg-white dark:!bg-gray-800" />
              </div>
            </div>
          </div>
        </div>
        
        {/* USP Summary */}
        <div className="bg-gradient-to-r from-gray-900 to-slate-800 rounded-2xl p-8 text-white mt-12">
          <h2 className="text-2xl font-bold text-center mb-6">Why We Should Win 🏆</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
                <Brain className="w-8 h-8" />
              </div>
              <h3 className="font-bold text-lg">Best AI</h3>
              <p className="text-sm text-gray-400 mt-2">
                Real ML models for anomaly detection, predictive maintenance, and smart recommendations.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mb-4">
                <Users className="w-8 h-8" />
              </div>
              <h3 className="font-bold text-lg">Best Impact</h3>
              <p className="text-sm text-gray-400 mt-2">
                Designed for rural India. Voice alerts in local languages, SMS support, offline-first.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center mb-4">
                <Star className="w-8 h-8" />
              </div>
              <h3 className="font-bold text-lg">Best Design</h3>
              <p className="text-sm text-gray-400 mt-2">
                Modern glassmorphism UI, gamification, real-time visualizations, and micro-interactions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;
