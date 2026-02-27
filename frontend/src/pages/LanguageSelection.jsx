import React, { useState } from 'react';
import { Globe, Check, ChevronRight } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useTheme } from '../contexts/ThemeContext';

const LanguageSelection = ({ onLanguageSelected }) => {
  const { language, changeLanguage, availableLanguages } = useLanguage();
  const { isDark } = useTheme();
  const [selectedLang, setSelectedLang] = useState(language);
  const [loading, setLoading] = useState(false);

  const handleLanguageSelect = async (langCode) => {
    setSelectedLang(langCode);
  };

  const handleContinue = async () => {
    setLoading(true);
    await changeLanguage(selectedLang);
    setTimeout(() => {
      if (onLanguageSelected) {
        onLanguageSelected();
      }
    }, 500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-mint-50/50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-2xl shadow-emerald-500/30 mb-6 animate-bounce-slow">
            <Globe className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-3">
            Gram Meter
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 font-medium">
            Choose Your Language / अपनी भाषा चुनें
          </p>
          <p className="text-lg text-slate-500 dark:text-slate-500 mt-2">
            Select your preferred language to continue
          </p>
        </div>

        {/* Language Selection Card */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-700 p-6 md:p-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Globe className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              Select Language
            </h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              {availableLanguages.length} languages available
            </p>
          </div>

          {/* Language Grid - Large, accessible buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
            {availableLanguages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageSelect(lang.code)}
                className={`relative p-5 rounded-2xl border-2 transition-all duration-200 text-left ${
                  selectedLang === lang.code
                    ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30 shadow-lg scale-105'
                    : 'border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 hover:border-emerald-300 hover:shadow-md'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-xl font-bold text-slate-900 dark:text-white mb-1">
                      {lang.nativeName}
                    </div>
                    <div className="text-sm text-slate-500 dark:text-slate-400">
                      {lang.name}
                    </div>
                  </div>
                  {selectedLang === lang.code && (
                    <div className="flex-shrink-0 ml-3">
                      <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center">
                        <Check className="w-5 h-5 text-white" strokeWidth={3} />
                      </div>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Continue Button - Large and prominent */}
          <button
            onClick={handleContinue}
            disabled={loading}
            className="w-full py-5 px-6 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 disabled:from-slate-400 disabled:to-slate-500 text-white font-bold text-xl rounded-2xl shadow-xl shadow-emerald-500/30 hover:shadow-2xl hover:shadow-emerald-500/40 transform hover:-translate-y-1 disabled:transform-none transition-all duration-200 flex items-center justify-center gap-3 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                Loading...
              </>
            ) : (
              <>
                Continue / जारी रखें
                <ChevronRight className="w-6 h-6" />
              </>
            )}
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-6 text-center">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            You can change the language anytime from settings
          </p>
        </div>
      </div>
    </div>
  );
};

export default LanguageSelection;
