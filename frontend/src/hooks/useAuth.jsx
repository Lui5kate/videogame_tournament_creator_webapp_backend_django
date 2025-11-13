import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

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
    const token = localStorage.getItem('access_token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/auth/profile/');
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login/', credentials);
      const { user, tokens } = response.data;
      
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      
      setUser(user);
      return user;
    } catch (error) {
      const message = error.response?.data?.non_field_errors?.[0] || 
                     error.response?.data?.detail || 
                     'Error al iniciar sesión';
      throw new Error(message);
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register/', userData);
      const { user, tokens } = response.data;
      
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      
      setUser(user);
      return user;
    } catch (error) {
      const message = error.response?.data?.username?.[0] ||
                     error.response?.data?.attuid?.[0] ||
                     error.response?.data?.non_field_errors?.[0] ||
                     'Error al registrarse';
      throw new Error(message);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const isAdmin = () => {
    return user?.user_type === 'admin';
  };

  const isPlayer = () => {
    return user?.user_type === 'player';
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAdmin,
    isPlayer,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
