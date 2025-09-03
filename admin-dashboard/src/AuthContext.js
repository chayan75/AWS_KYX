import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication on app load
    const checkAuth = () => {
      const token = localStorage.getItem('authToken');
      const userInfo = localStorage.getItem('userInfo');
      
      if (token && userInfo) {
        try {
          const userData = JSON.parse(userInfo);
          setUser(userData);
        } catch (error) {
          console.error('Error parsing user info:', error);
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = (userData) => {
    setUser(userData);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('sessionId');
    localStorage.removeItem('userInfo');
  };

  const isAdmin = () => {
    return user?.role === 'admin';
  };

  const isUser = () => {
    return user?.role === 'user';
  };

  const hasPermission = (action) => {
    if (!user) return false;
    
    if (user.role === 'admin') {
      return true; // Admin can do everything
    }
    
    if (user.role === 'user') {
      // User can only view, not modify
      const readOnlyActions = [
        'view_dashboard',
        'view_case_details',
        'view_documents',
        'view_audit_logs',
        'view_email_history'
      ];
      return readOnlyActions.includes(action);
    }
    
    return false;
  };

  const value = {
    user,
    login,
    logout,
    isAdmin,
    isUser,
    hasPermission,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 