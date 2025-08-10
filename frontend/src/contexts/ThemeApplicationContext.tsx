import React, { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { ThemeProvider, type Theme } from '@mui/material/styles';
import { useThemeApplication } from '../hooks/useThemeApplication';
import { useTheme } from './useTheme';
import { getThemeConfig } from './theme-constants';

interface ThemeApplicationContextType {
  previewTheme: (themeId: string) => Promise<void>;
  applyTheme: (themeId: string) => Promise<void>;
  clearPreview: () => void;
  isApplying: boolean;
  appliedTheme: string | null;
}

// Create the context
const ThemeApplicationContext = createContext<ThemeApplicationContextType | undefined>(undefined);

interface ThemeApplicationProviderProps {
  children: ReactNode;
}

export const ThemeApplicationProvider: React.FC<ThemeApplicationProviderProps> = ({ children }) => {
  const baseTheme = useTheme();
  const {
    isApplying,
    appliedTheme,
    previewTheme,
    previewThemeById,
    applyTheme: applyThemeHook,
    clearPreview,
    loadSavedTheme,
  } = useThemeApplication();

  // State to track the actual theme to use
  const [currentTheme, setCurrentTheme] = useState<Theme>(() => 
    getThemeConfig(baseTheme.isDark ? 'dark' : 'light')
  );

  // Update current theme when base theme changes or preview theme changes
  useEffect(() => {
    if (previewTheme) {
      setCurrentTheme(previewTheme);
    } else {
      setCurrentTheme(getThemeConfig(baseTheme.isDark ? 'dark' : 'light'));
    }
  }, [previewTheme, baseTheme.isDark]);

  // Load saved theme on mount
  useEffect(() => {
    loadSavedTheme();
  }, [loadSavedTheme]);

  const contextValue: ThemeApplicationContextType = {
    previewTheme: previewThemeById,
    applyTheme: applyThemeHook,
    clearPreview,
    isApplying,
    appliedTheme,
  };

  return (
    <ThemeApplicationContext.Provider value={contextValue}>
      <ThemeProvider theme={currentTheme}>{children}</ThemeProvider>
    </ThemeApplicationContext.Provider>
  );
};

// Custom hook to use the theme application context
export const useThemeApplication_Context = (): ThemeApplicationContextType => {
  const context = useContext(ThemeApplicationContext);
  if (!context) {
    throw new Error('useThemeApplication must be used within a ThemeApplicationProvider');
  }
  return context;
};

export default ThemeApplicationContext;
