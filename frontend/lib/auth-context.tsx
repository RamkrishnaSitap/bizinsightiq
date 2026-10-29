'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { UserProfile, AuthResponse } from './types';
import { authApi, setAuthToken, removeAuthToken } from './api';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Rehydrate token from client storage
    const savedToken = localStorage.getItem('bizinsightiq_jwt');
    const savedUser = localStorage.getItem('bizinsightiq_user');

    if (savedToken && savedToken !== 'undefined' && savedToken !== 'null' && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch {
        removeAuthToken();
      }
    } else if (savedToken === 'undefined' || savedToken === 'null') {
      removeAuthToken();
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const authData: AuthResponse = await authApi.login({ username, password });
      const jwtToken = authData.accessToken || authData.token;

      if (!jwtToken) {
        throw new Error('Authentication failed: No access token received from server.');
      }

      const userProfile: UserProfile = {
        id: authData.user?.id || '',
        username: authData.user?.username || authData.username || username,
        email: authData.user?.email || authData.email || '',
        role: authData.user?.role || authData.role || 'ROLE_ANALYST',
      };

      setAuthToken(jwtToken);
      localStorage.setItem('bizinsightiq_user', JSON.stringify(userProfile));

      setToken(jwtToken);
      setUser(userProfile);
      router.push('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    removeAuthToken();
    setToken(null);
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
