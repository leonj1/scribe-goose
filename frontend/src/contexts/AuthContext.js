/**
 * Authentication context for managing user authentication state.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    const token = authApi.getToken();
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  const login = () => {
    authApi.login();
  };

  const logout = async () => {
    try {
      await authApi.logout();
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local auth state even if API call fails
      setIsAuthenticated(false);
    }
  };

  const handleAuthCallback = (token) => {
    authApi.setToken(token);
    setIsAuthenticated(true);
  };

  const value = {
    isAuthenticated,
    loading,
    login,
    logout,
    handleAuthCallback,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
