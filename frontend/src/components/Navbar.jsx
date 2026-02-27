// Navbar Component with Dynamic Language Support
import React, { useState } from 'react';
import { User, Globe, Wifi, WifiOff, ChevronDown, Loader, Moon, Sun, LogOut } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useTheme } from '../contexts/ThemeContext';

const Navbar = ({ isOffline, logo, onLogout }) => {
  const { language, changeLanguage, t, availableLanguages, loading } = useLanguage();
  const { isDark, toggleTheme } = useTheme();
  const [languageMenuOpen, setLanguageMenuOpen] = useState(false);

  const handleLanguageChange = async (langCode) => {
    setLanguageMenuOpen(false);
    await changeLanguage(langCode);
  };

  return (
    <nav className="sticky top-0 z-50 bg-emerald-500/90 dark:bg-slate-800/90 backdrop-blur-lg text-white p-4 shadow-lg border-b border-emerald-400/30 dark:border-slate-700/50">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo and Title */}
        <button 
          onClick={() => window.location.reload()} 
          className="flex items-center gap-3 cursor-pointer hover:opacity-90 transition-opacity"
        >
          <div className="bg-white/20 backdrop-blur-sm p-2 rounded-xl shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }}>
            {logo ? (
              <img 
                src={logo} 
                alt="Gram Meter Logo" 
                className="h-8 w-8 object-contain" 
                style={{ filter: 'none', opacity: 1, mixBlendMode: 'normal' }} 
              />
            ) : (
              <div className="h-8 w-8 bg-emerald-300 rounded-lg" />
            )}
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wide text-white">{t('title')}</h1>
            <p className="text-xs text-emerald-100 opacity-80">{t('poweredBy')}</p>
          </div>
        </button>

        {/* Right Side Actions */}
        <div className="flex items-center gap-4">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 bg-white/20 hover:bg-white/30 dark:bg-slate-700 dark:hover:bg-slate-600 rounded-lg transition-all"
            aria-label="Toggle dark mode"
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {/* Network Status Indicator */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
            isOffline 
              ? 'bg-red-500/20 text-red-100' 
              : 'bg-emerald-600/20 text-emerald-100'
          }`}>
            {isOffline ? (
              <>
                <WifiOff size={16} />
                <span className="text-xs font-medium hidden sm:inline">{t('offline')}</span>
              </>
            ) : (
              <>
                <Wifi size={16} />
                <span className="text-xs font-medium hidden sm:inline">{t('online')}</span>
              </>
            )}
          </div>

          {/* Language Selector with All Indian Languages */}
          <div className="relative">
            <button 
              onClick={() => setLanguageMenuOpen(!languageMenuOpen)}
              className="flex items-center gap-2 px-3 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-all min-w-[120px] justify-between"
              disabled={loading}
            >
              <Globe size={18} />
              <span className="text-sm font-medium">
                {availableLanguages.find(l => l.code === language)?.nativeName || 'English'}
              </span>
              {loading ? (
                <Loader size={16} className="animate-spin" />
              ) : (
                <ChevronDown size={16} className={`transition-transform ${languageMenuOpen ? 'rotate-180' : ''}`} />
              )}
            </button>

            {/* Language Dropdown - All Indian Languages */}
            {languageMenuOpen && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setLanguageMenuOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-glass-lg border border-slate-100 dark:border-slate-700 overflow-hidden z-50 max-h-96 overflow-y-auto custom-scrollbar">
                  <div className="p-2 bg-emerald-50 dark:bg-slate-700 border-b border-emerald-100 dark:border-slate-600">
                    <p className="text-xs font-semibold text-emerald-800 dark:text-emerald-300 uppercase tracking-wide">
                      Select Language
                    </p>
                    <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-0.5">
                      {availableLanguages.length} Indian Languages
                    </p>
                  </div>
                  {availableLanguages.map(lang => (
                    <button
                      key={lang.code}
                      onClick={() => handleLanguageChange(lang.code)}
                      disabled={loading}
                      className={`w-full text-left px-4 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                        language === lang.code
                          ? 'bg-emerald-50 dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 font-semibold'
                          : 'text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{lang.nativeName}</div>
                          <div className="text-xs text-slate-500 dark:text-slate-400">{lang.name}</div>
                        </div>
                        {language === lang.code && (
                          <div className="h-2 w-2 bg-emerald-500 rounded-full" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* User Menu */}
          {onLogout && (
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-white rounded-lg transition-all"
              title="Logout"
            >
              <LogOut size={18} />
              <span className="text-sm font-medium hidden sm:inline">Logout</span>
            </button>
          )}
          {!onLogout && (
            <div className="h-10 w-10 bg-gradient-to-tr from-emerald-400 to-teal-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white/50 cursor-pointer hover:scale-110 transition-transform">
              <User size={20} className="text-white" />
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
