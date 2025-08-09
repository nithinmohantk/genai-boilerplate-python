import React, { createContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import {
  type ThemeMode,
  getThemeConfig,
  getEffectiveMode,
} from './theme-constants';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
  isDark: boolean;
}

// Create the context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Export the ThemeMode type for external use
export type { ThemeMode };

interface ThemeContextProviderProps {
  children: ReactNode;
}

export const CustomThemeProvider: React.FC<ThemeContextProviderProps> = ({ children }) => {
  // Initialize theme from localStorage or default to 'auto'
  const [mode, setMode] = useState<ThemeMode>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme-mode');
      return (saved as ThemeMode) || 'auto';
    }
    return 'auto';
  });

  // Get effective mode for theme creation
  const effectiveMode = getEffectiveMode(mode);
  const isDark = effectiveMode === 'dark';

  // Create theme based on effective mode
  const theme = getThemeConfig(effectiveMode);

  // Save mode to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('theme-mode', mode);
  }, [mode]);

  // Listen for system theme changes when in auto mode
  useEffect(() => {
    if (mode === 'auto' && typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => {
        // Force a re-render by updating the state
        setMode('auto');
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => {
      if (prevMode === 'light') return 'dark';
      if (prevMode === 'dark') return 'auto';
      return 'light'; // auto -> light
    });
  };

  const setTheme = (newMode: ThemeMode) => {
    setMode(newMode);
  };

  const contextValue: ThemeContextType = {
    mode,
    toggleTheme,
    setTheme,
    isDark,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
