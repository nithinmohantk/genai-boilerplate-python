import React, { createContext, useContext, useState, useEffect } from 'react';
import { ThemeProvider, createTheme, type Theme } from '@mui/material/styles';
import type { ReactNode } from 'react';

export type ThemeMode = 'light' | 'dark' | 'auto';

interface SimplifiedThemeContextType {
  mode: ThemeMode;
  setTheme: (mode: ThemeMode) => void;
  toggleTheme: () => void;
  isDark: boolean;
}

const SimplifiedThemeContext = createContext<SimplifiedThemeContextType | undefined>(undefined);

interface SimplifiedThemeProviderProps {
  children: ReactNode;
}

export const SimplifiedThemeProvider: React.FC<SimplifiedThemeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme-mode');
      return (saved as ThemeMode) || 'auto';
    }
    return 'auto';
  });

  // Get effective mode (resolve 'auto' to actual light/dark)
  const getEffectiveMode = (): 'light' | 'dark' => {
    if (mode === 'auto') {
      if (typeof window !== 'undefined' && window.matchMedia) {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      return 'light';
    }
    return mode;
  };

  const effectiveMode = getEffectiveMode();
  const isDark = effectiveMode === 'dark';

  // Create MUI theme based on effective mode
  const theme: Theme = createTheme({
    palette: {
      mode: effectiveMode,
      ...(effectiveMode === 'dark' ? {
        primary: {
          main: '#90caf9',
        },
        secondary: {
          main: '#f48fb1',
        },
        background: {
          default: '#121212',
          paper: '#1e1e1e',
        },
      } : {
        primary: {
          main: '#1976d2',
        },
        secondary: {
          main: '#dc004e',
        },
      }),
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
          },
        },
      },
    },
  });

  // Save to localStorage when mode changes
  useEffect(() => {
    localStorage.setItem('theme-mode', mode);
  }, [mode]);

  // Listen for system theme changes when in auto mode
  useEffect(() => {
    if (mode === 'auto' && typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => {
        // Force re-render by triggering a state update
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

  const contextValue: SimplifiedThemeContextType = {
    mode,
    setTheme,
    toggleTheme,
    isDark,
  };

  return (
    <SimplifiedThemeContext.Provider value={contextValue}>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </SimplifiedThemeContext.Provider>
  );
};

// Custom hook to use the simplified theme context
export const useSimplifiedTheme = (): SimplifiedThemeContextType => {
  const context = useContext(SimplifiedThemeContext);
  if (!context) {
    throw new Error('useSimplifiedTheme must be used within a SimplifiedThemeProvider');
  }
  return context;
};
