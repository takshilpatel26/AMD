import React, { Suspense, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { LanguageProvider } from './contexts/LanguageContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Dashboard from './pages/Dashboard';
import Auth from './pages/Auth';
import LanguageSelection from './pages/LanguageSelection';
import Analytics from './pages/Analytics';
import Meters from './pages/Meters';
import Alerts from './pages/Alerts';
import Billing from './pages/Billing';
import Profile from './pages/Profile';
import CompanyAdminDashboard from './pages/CompanyAdminDashboard';
import AdminAuth from './pages/AdminAuth';
import AdminDashboard from './pages/AdminDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary';
import authService from './services/authService';
import Layout from './components/Layout';

function App() {
  // Check if user is already authenticated
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  const [languageSelected, setLanguageSelected] = useState(() => {
    // Check if language was previously selected
    return localStorage.getItem('languageSelected') === 'true';
  });

  useEffect(() => {
    // Verify auth status on mount
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          await authService.checkAuthStatus();
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Auth check failed:', error);
          setIsAuthenticated(false);
        }
      }
    };
    checkAuth();
  }, []);

  const handleAuthSuccess = (user) => {
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleLanguageSelected = () => {
    localStorage.setItem('languageSelected', 'true');
    setLanguageSelected(true);
  };

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <Router>
            <Suspense fallback={
              <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-mint-50/50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center">
                <LoadingSpinner size="large" text="Loading Gram Meter..." />
              </div>
            }>
              <Routes>
                <Route 
                  path="/language" 
                  element={
                    languageSelected ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <LanguageSelection onLanguageSelected={handleLanguageSelected} />
                    )
                  } 
                />
                <Route 
                  path="/auth" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : isAuthenticated ? (
                      <Navigate to="/dashboard" replace />
                    ) : (
                      <Auth onAuthSuccess={handleAuthSuccess} />
                    )
                  } 
                />
                
                {/* Protected Routes with Layout */}
                <Route 
                  path="/dashboard" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : !isAuthenticated ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <Layout onLogout={handleLogout}>
                        <Dashboard />
                      </Layout>
                    )
                  } 
                />
                <Route 
                  path="/analytics" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : !isAuthenticated ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <Layout onLogout={handleLogout}>
                        <Analytics />
                      </Layout>
                    )
                  } 
                />
                <Route 
                  path="/meters" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : !isAuthenticated ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <Layout onLogout={handleLogout}>
                        <Meters />
                      </Layout>
                    )
                  } 
                />
                <Route 
                  path="/alerts" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : !isAuthenticated ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <Layout onLogout={handleLogout}>
                        <Alerts />
                      </Layout>
                    )
                  } 
                />
                <Route 
                  path="/billing" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : !isAuthenticated ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <Layout onLogout={handleLogout}>
                        <Billing />
                      </Layout>
                    )
                  } 
                />
                <Route 
                  path="/profile" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : !isAuthenticated ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <Layout onLogout={handleLogout}>
                        <Profile />
                      </Layout>
                    )
                  } 
                />
                <Route 
                  path="/settings" 
                  element={
                    !languageSelected ? (
                      <Navigate to="/language" replace />
                    ) : !isAuthenticated ? (
                      <Navigate to="/auth" replace />
                    ) : (
                      <Layout onLogout={handleLogout}>
                        <Profile />
                      </Layout>
                    )
                  } 
                />
                <Route 
                  path="/admin/distribution" 
                  element={<CompanyAdminDashboard />}
                />
                <Route 
                  path="/admin" 
                  element={<AdminAuth />}
                />
                <Route 
                  path="/admin/dashboard" 
                  element={<AdminDashboard />}
                />
                <Route 
                  path="/" 
                  element={
                    <Navigate 
                      to={
                      !languageSelected 
                        ? "/language" 
                        : isAuthenticated 
                        ? "/dashboard" 
                        : "/auth"
                    } 
                    replace 
                  />
                } 
              />
            </Routes>
          </Suspense>
          
          {/* Toast Notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              className: 'dark:bg-slate-700 dark:text-white',
              style: {
                background: '#1e293b',
                color: '#fff',
                borderRadius: '12px',
                padding: '16px',
                fontSize: '14px',
                fontWeight: '500',
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.3)',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Router>
      </LanguageProvider>
    </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;