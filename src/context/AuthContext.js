import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

const TOKEN_KEY = 'diet_auth_token';

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
      // Restore user data from localStorage if available
      const storedUserData = localStorage.getItem('diet_user_data');
      if (storedUserData) {
        try {
          const userData = JSON.parse(storedUserData);
          setUser(userData);
        } catch (error) {
          console.error('Failed to restore user data:', error);
          localStorage.removeItem('diet_user_data');
        }
      }
    } else {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem('diet_user_data');
      setUser(null);
    }
  }, [token]);

  async function parseApiResponse(res) {
    const text = await res.text();
    if (!text) {
      return {};
    }
    try {
      return JSON.parse(text);
    } catch {
      const preview = text.replace(/\s+/g, ' ').slice(0, 180);
      throw new Error(
        res.ok
          ? 'Invalid response from server'
          : `Server returned non-JSON (${res.status}): ${preview || 'empty body'}`
      );
    }
  }

  const login = async (email, password) => {
    let res;
    try {
      res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
    } catch (e) {
      throw new Error(
        e.message === 'Failed to fetch'
          ? 'Cannot reach the API. Start the Flask backend (port 5000) and use npm start with proxy.'
          : e.message
      );
    }
    const data = await parseApiResponse(res);
    if (!res.ok) {
      throw new Error(data.error || `Login failed (${res.status})`);
    }
    if (!data.token) {
      throw new Error('Login response missing token');
    }
    setTokenState(data.token);
    setUser(data.user);
    
    // Store complete user data in localStorage for persistence
    localStorage.setItem('diet_user_data', JSON.stringify(data.user));
    
    return data;
  };

  const register = async (payload) => {
    let res;
    try {
      // Combine first and last name
      const name = `${payload.firstName} ${payload.lastName}`;
      
      // Prepare registration payload for backend
      const registrationData = {
        name: name,
        email: payload.email,
        password: payload.password,
        age: payload.age,
        gender: payload.gender,
        phone: payload.phone,
        // Don't set default weight/height - user will fill in diet plan
        activity_level: 'moderate', // Default, will be updated in diet form
        goal: 'maintenance', // Default, will be updated in diet form
      };

      res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registrationData),
      });
    } catch (e) {
      throw new Error(
        e.message === 'Failed to fetch'
          ? 'Cannot reach the API. Start the Flask backend (port 5000) and use npm start with proxy.'
          : e.message
      );
    }
    const data = await parseApiResponse(res);
    if (!res.ok) {
      throw new Error(data.error || `Registration failed (${res.status})`);
    }
    if (!data.token) {
      throw new Error('Registration response missing token');
    }
    setTokenState(data.token);
    setUser(data.user);
    
    // Store complete user data in localStorage for persistence
    localStorage.setItem('diet_user_data', JSON.stringify(data.user));
    
    return data;
  };

  const logout = useCallback(() => {
    setTokenState(null);
    setUser(null);
    // Clear stored user data
    localStorage.removeItem('diet_user_data');
  }, []);

  const authFetch = useCallback(
    async (path, options = {}) => {
      const headers = {
        ...(options.headers || {}),
      };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
      }
      const body =
        options.body && typeof options.body === 'object' && !(options.body instanceof FormData)
          ? JSON.stringify(options.body)
          : options.body;
      const res = await fetch(path, { ...options, headers, body });
      return res;
    },
    [token]
  );

  const value = {
    token,
    user,
    isAuthenticated: !!token,
    login,
    register,
    logout,
    authFetch,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
