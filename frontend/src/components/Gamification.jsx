// Gamification Component - Energy Saving Achievements & Community Features
import React, { useState, useEffect, useMemo } from 'react';
import {
  Trophy,
  Medal,
  Star,
  Flame,
  Zap,
  Leaf,
  Target,
  Award,
  Crown,
  TrendingUp,
  TrendingDown,
  Users,
  ChevronRight,
  Lock,
  Sparkles,
  Gift,
  Calendar,
  CheckCircle2,
  Timer
} from 'lucide-react';

// Achievement Badge Component
const AchievementBadge = ({ achievement, unlocked, progress = 0, onClick }) => {
  const Icon = achievement.icon;
  
  return (
    <div 
      onClick={onClick}
      className={`relative group cursor-pointer transition-all duration-300 ${
        unlocked ? 'hover:scale-105' : 'opacity-60 hover:opacity-80'
      }`}
    >
      <div className={`w-20 h-20 rounded-2xl flex items-center justify-center relative overflow-hidden ${
        unlocked 
          ? `bg-gradient-to-br ${achievement.gradient} shadow-lg` 
          : 'bg-gray-200 dark:bg-gray-700'
      }`}>
        {/* Glow effect for unlocked */}
        {unlocked && (
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        )}
        
        {/* Progress ring for locked */}
        {!unlocked && progress > 0 && (
          <svg className="absolute inset-0 w-full h-full -rotate-90">
            <circle
              cx="40"
              cy="40"
              r="36"
              stroke="currentColor"
              strokeWidth="4"
              fill="transparent"
              className="text-gray-300 dark:text-gray-600"
            />
            <circle
              cx="40"
              cy="40"
              r="36"
              stroke="#10b981"
              strokeWidth="4"
              fill="transparent"
              strokeDasharray={`${2 * Math.PI * 36}`}
              strokeDashoffset={`${2 * Math.PI * 36 * (1 - progress / 100)}`}
              strokeLinecap="round"
            />
          </svg>
        )}
        
        <Icon className={`w-8 h-8 relative z-10 ${
          unlocked ? 'text-white' : 'text-gray-400 dark:text-gray-500'
        }`} />
        
        {/* Lock icon */}
        {!unlocked && (
          <div className="absolute bottom-1 right-1 p-1 bg-gray-300 dark:bg-gray-600 rounded-full">
            <Lock className="w-3 h-3 text-gray-500 dark:text-gray-400" />
          </div>
        )}
        
        {/* Level indicator */}
        {unlocked && achievement.level && (
          <div className="absolute -top-1 -right-1 px-2 py-0.5 bg-yellow-400 rounded-full text-xs font-bold text-yellow-900">
            Lv.{achievement.level}
          </div>
        )}
      </div>
      
      <p className={`text-xs text-center mt-2 font-medium ${
        unlocked ? 'text-gray-900 dark:text-white' : 'text-gray-500'
      }`}>
        {achievement.name}
      </p>
      
      {/* Tooltip on hover */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none w-40 text-center z-20">
        <p className="font-semibold">{achievement.name}</p>
        <p className="text-gray-300 mt-1">{achievement.description}</p>
        {!unlocked && <p className="text-emerald-400 mt-1">{progress}% complete</p>}
      </div>
    </div>
  );
};

// Leaderboard User Row
const LeaderboardRow = ({ rank, user, isCurrentUser }) => {
  const getRankIcon = (r) => {
    if (r === 1) return <Crown className="w-5 h-5 text-yellow-500" />;
    if (r === 2) return <Medal className="w-5 h-5 text-gray-400" />;
    if (r === 3) return <Medal className="w-5 h-5 text-amber-600" />;
    return <span className="w-5 h-5 flex items-center justify-center text-sm font-bold text-gray-500">#{r}</span>;
  };
  
  return (
    <div className={`flex items-center gap-4 p-3 rounded-xl transition-colors ${
      isCurrentUser 
        ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800' 
        : 'hover:bg-gray-50 dark:hover:bg-gray-800'
    }`}>
      <div className="flex items-center justify-center w-8">
        {getRankIcon(rank)}
      </div>
      
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white font-bold">
        {user.name.charAt(0)}
      </div>
      
      <div className="flex-1">
        <p className={`font-semibold ${isCurrentUser ? 'text-emerald-700 dark:text-emerald-400' : 'text-gray-900 dark:text-white'}`}>
          {user.name} {isCurrentUser && <span className="text-xs">(You)</span>}
        </p>
        <p className="text-xs text-gray-500">{user.village}</p>
      </div>
      
      <div className="text-right">
        <p className="font-bold text-emerald-600 dark:text-emerald-400">{user.savings}%</p>
        <p className="text-xs text-gray-500">saved</p>
      </div>
      
      <div className="flex items-center gap-1">
        <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
        <span className="font-semibold text-gray-900 dark:text-white">{user.points}</span>
      </div>
    </div>
  );
};

// Streak Counter
const StreakCounter = ({ days, maxDays = 30 }) => {
  return (
    <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl p-4 text-white">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-xl">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm opacity-90">Energy Saving Streak</p>
            <p className="text-3xl font-bold">{days} days</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm opacity-90">Target</p>
          <p className="text-xl font-bold">{maxDays} days</p>
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="mt-4 h-2 bg-white/30 rounded-full overflow-hidden">
        <div 
          className="h-full bg-white rounded-full transition-all duration-500"
          style={{ width: `${(days / maxDays) * 100}%` }}
        />
      </div>
      
      {/* Day indicators */}
      <div className="flex justify-between mt-2 text-xs opacity-75">
        <span>Day 1</span>
        <span>Day {Math.round(maxDays / 2)}</span>
        <span>Day {maxDays}</span>
      </div>
    </div>
  );
};

// Daily Challenge Card
const DailyChallenge = ({ challenge, onComplete }) => {
  const [timeLeft, setTimeLeft] = useState('');
  
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const endOfDay = new Date(now);
      endOfDay.setHours(23, 59, 59, 999);
      const diff = endOfDay - now;
      
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      setTimeLeft(`${hours}h ${minutes}m`);
    };
    
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="bg-gradient-to-r from-violet-500/10 to-purple-500/10 dark:from-violet-900/30 dark:to-purple-900/30 rounded-xl p-4 border border-violet-200 dark:border-violet-800">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Gift className="w-5 h-5 text-violet-600 dark:text-violet-400" />
          <span className="font-semibold text-violet-700 dark:text-violet-300">Daily Challenge</span>
        </div>
        <div className="flex items-center gap-1 text-sm text-violet-600 dark:text-violet-400">
          <Timer className="w-4 h-4" />
          {timeLeft}
        </div>
      </div>
      
      <p className="text-gray-800 dark:text-gray-200 font-medium mb-2">{challenge.title}</p>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{challenge.description}</p>
      
      {/* Progress */}
      <div className="flex items-center gap-3 mb-3">
        <div className="flex-1 h-2 bg-violet-200 dark:bg-violet-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full transition-all"
            style={{ width: `${challenge.progress}%` }}
          />
        </div>
        <span className="text-sm font-medium text-violet-600 dark:text-violet-400">
          {challenge.progress}%
        </span>
      </div>
      
      {/* Reward */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            +{challenge.reward} points
          </span>
        </div>
        {challenge.progress >= 100 ? (
          <button 
            onClick={onComplete}
            className="px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-lg text-sm font-semibold hover:from-violet-600 hover:to-purple-700 transition-all flex items-center gap-1"
          >
            <CheckCircle2 className="w-4 h-4" />
            Claim
          </button>
        ) : (
          <span className="text-sm text-gray-500">In Progress</span>
        )}
      </div>
    </div>
  );
};

const Gamification = ({ userStats, className = '' }) => {
  const [activeTab, setActiveTab] = useState('achievements');
  
  // Mock achievements data
  const achievements = [
    { id: 1, name: 'First Save', icon: Leaf, gradient: 'from-emerald-400 to-green-500', description: 'Save energy for the first time', unlocked: true, level: 1 },
    { id: 2, name: 'Week Warrior', icon: Flame, gradient: 'from-orange-400 to-red-500', description: '7-day saving streak', unlocked: true, level: 2 },
    { id: 3, name: 'Efficiency Expert', icon: Target, gradient: 'from-blue-400 to-indigo-500', description: 'Maintain 90%+ efficiency', unlocked: true, level: 1 },
    { id: 4, name: 'Power Saver', icon: Zap, gradient: 'from-yellow-400 to-amber-500', description: 'Reduce consumption by 20%', unlocked: false, progress: 75 },
    { id: 5, name: 'Night Owl', icon: Star, gradient: 'from-violet-400 to-purple-500', description: 'Use 80% power during off-peak', unlocked: false, progress: 45 },
    { id: 6, name: 'Green Champion', icon: Award, gradient: 'from-teal-400 to-cyan-500', description: 'Save 100 kg CO2', unlocked: false, progress: 30 },
    { id: 7, name: 'Community Leader', icon: Users, gradient: 'from-pink-400 to-rose-500', description: 'Top 10 in leaderboard', unlocked: false, progress: 60 },
    { id: 8, name: 'Master Saver', icon: Crown, gradient: 'from-amber-400 to-yellow-500', description: 'Complete all achievements', unlocked: false, progress: 25 },
  ];
  
  // Mock leaderboard data
  const leaderboard = [
    { id: 1, name: 'Ramesh Kumar', village: 'Rajkot', savings: 32, points: 4520 },
    { id: 2, name: 'Suresh Patel', village: 'Ahmedabad', savings: 28, points: 4100 },
    { id: 3, name: 'Mahesh Singh', village: 'Vadodara', savings: 25, points: 3890 },
    { id: 4, name: 'You', village: 'Surat', savings: 22, points: 3450 },
    { id: 5, name: 'Dinesh Shah', village: 'Jamnagar', savings: 20, points: 3200 },
    { id: 6, name: 'Kamlesh Joshi', village: 'Bhavnagar', savings: 18, points: 2980 },
    { id: 7, name: 'Nilesh Trivedi', village: 'Gandhinagar', savings: 15, points: 2750 },
  ];
  
  // Daily challenge
  const dailyChallenge = {
    id: 1,
    title: 'Off-Peak Champion',
    description: 'Run your irrigation pump only between 10 PM - 6 AM today',
    progress: 68,
    reward: 50
  };
  
  const unlockedCount = achievements.filter(a => a.unlocked).length;
  const totalPoints = 3450;
  const currentStreak = 12;
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-yellow-400 to-amber-500 rounded-xl p-4 text-white">
          <div className="flex items-center gap-2 mb-2">
            <Star className="w-5 h-5" />
            <span className="text-sm opacity-90">Total Points</span>
          </div>
          <p className="text-3xl font-bold">{totalPoints.toLocaleString()}</p>
          <p className="text-xs opacity-75 mt-1">Rank #4 in your area</p>
        </div>
        
        <div className="bg-gradient-to-br from-emerald-400 to-green-500 rounded-xl p-4 text-white">
          <div className="flex items-center gap-2 mb-2">
            <Trophy className="w-5 h-5" />
            <span className="text-sm opacity-90">Achievements</span>
          </div>
          <p className="text-3xl font-bold">{unlockedCount}/{achievements.length}</p>
          <p className="text-xs opacity-75 mt-1">{Math.round((unlockedCount/achievements.length)*100)}% unlocked</p>
        </div>
        
        <div className="bg-gradient-to-br from-violet-400 to-purple-500 rounded-xl p-4 text-white">
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-5 h-5" />
            <span className="text-sm opacity-90">Energy Saved</span>
          </div>
          <p className="text-3xl font-bold">22%</p>
          <p className="text-xs opacity-75 mt-1">This month vs last</p>
        </div>
      </div>
      
      {/* Streak Counter */}
      <StreakCounter days={currentStreak} maxDays={30} />
      
      {/* Daily Challenge */}
      <DailyChallenge 
        challenge={dailyChallenge} 
        onComplete={() => console.log('Challenge completed!')} 
      />
      
      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'achievements', label: 'Achievements', icon: Trophy },
          { id: 'leaderboard', label: 'Leaderboard', icon: Users },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab.id
                ? 'text-emerald-600 dark:text-emerald-400 border-emerald-600 dark:border-emerald-400'
                : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 border-transparent'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>
      
      {/* Tab Content */}
      {activeTab === 'achievements' && (
        <div className="grid grid-cols-4 gap-4">
          {achievements.map((achievement) => (
            <AchievementBadge
              key={achievement.id}
              achievement={achievement}
              unlocked={achievement.unlocked}
              progress={achievement.progress}
              onClick={() => console.log('Achievement clicked:', achievement.name)}
            />
          ))}
        </div>
      )}
      
      {activeTab === 'leaderboard' && (
        <div className="space-y-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">Gujarat Region - This Month</h3>
            <select className="text-sm bg-gray-100 dark:bg-gray-800 border-0 rounded-lg px-3 py-1.5">
              <option>This Month</option>
              <option>This Week</option>
              <option>All Time</option>
            </select>
          </div>
          
          {leaderboard.map((user, index) => (
            <LeaderboardRow
              key={user.id}
              rank={index + 1}
              user={user}
              isCurrentUser={user.name === 'You'}
            />
          ))}
          
          <button className="w-full py-3 text-sm font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 rounded-lg transition-colors flex items-center justify-center gap-2">
            View Full Leaderboard
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};

export default Gamification;
