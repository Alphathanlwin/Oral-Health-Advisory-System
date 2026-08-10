import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext(null);

const TOKEN_KEY = 'ohas_token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const decodeToken = useCallback((token) => {
    try {
      const decoded = jwtDecode(token);
      return {
        id: decoded.sub,
        exp: decoded.exp,
      };
    } catch (error) {
      return null;
    }
  }, []);

  const isTokenValid = useCallback((token) => {
    if (!token) return false;
    
    try {
      const decoded = jwtDecode(token);
      const now = Date.now() / 1000;
      return decoded.exp > now;
    } catch (error) {
      return false;
    }
  }, []);

  const login = useCallback((accessToken, userData) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    setToken(accessToken);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const checkAuth = useCallback(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    
    if (storedToken && isTokenValid(storedToken)) {
      const decoded = decodeToken(storedToken);
      if (decoded) {
        setToken(storedToken);
        setUser({ id: decoded.id });
        return true;
      }
    }
    
    logout();
    return false;
  }, [decodeToken, isTokenValid, logout]);

  useEffect(() => {
    checkAuth();
    setLoading(false);
  }, [checkAuth]);

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    logout,
    checkAuth,
    setUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export { AuthContext };
