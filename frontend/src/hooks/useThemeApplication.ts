import { useState, useCallback } from 'react';
import { createTheme, type Theme } from '@mui/material/styles';
import { useTheme as useThemeContext } from '../contexts/useTheme';

// Types for backend theme data
export interface BackendTheme {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  color_scheme?: {
    light: {
      primary: string;
      secondary: string;
      background: string;
      text: string;
    };
    dark: {
      primary: string;
      secondary: string;
      background: string;
      text: string;
    };
  };
}

// Custom hook for theme application
export const useThemeApplication = () => {
  const [isApplying, setIsApplying] = useState(false);
  const [appliedTheme, setAppliedTheme] = useState<string | null>(null);
  const [previewTheme, setPreviewTheme] = useState<Theme | null>(null);
  const themeContext = useThemeContext();

  // Fetch theme details from backend
  const fetchThemeDetails = useCallback(async (themeId: string): Promise<BackendTheme> => {
    const response = await fetch(`http://localhost:8000/api/v1/themes/${themeId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch theme: ${themeId}`);
    }
    return response.json();
  }, []);

  // Convert backend theme to MUI theme
  const createMUITheme = useCallback((backendTheme: BackendTheme, isDark: boolean): Theme => {
    const colorScheme = backendTheme.color_scheme;
    if (!colorScheme) {
      // Fallback to default theme if no color scheme
      return createTheme({ palette: { mode: isDark ? 'dark' : 'light' } });
    }

    const scheme = isDark ? colorScheme.dark : colorScheme.light;
    
    return createTheme({
      palette: {
        mode: isDark ? 'dark' : 'light',
        primary: {
          main: scheme.primary,
          light: isDark ? '#8b5cf6' : '#60a5fa',
          dark: isDark ? '#4f46e5' : '#2563eb',
        },
        secondary: {
          main: scheme.secondary,
          light: isDark ? '#c084fc' : '#a78bfa',
          dark: isDark ? '#9333ea' : '#7c3aed',
        },
        background: {
          default: scheme.background,
          paper: isDark ? '#1e293b' : '#ffffff',
        },
        text: {
          primary: scheme.text,
          secondary: isDark ? '#94a3b8' : '#64748b',
        },
        divider: isDark ? '#334155' : '#e2e8f0',
        action: {
          hover: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
          selected: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)',
        },
      },
      typography: {
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      },
      shape: {
        borderRadius: 12,
      },
      components: {
        MuiCssBaseline: {
          styleOverrides: {
            body: {
              backgroundColor: scheme.background,
              color: scheme.text,
              transition: 'background-color 0.3s ease-in-out, color 0.3s ease-in-out',
            },
            '#root': {
              minHeight: '100vh',
              backgroundColor: scheme.background,
              color: scheme.text,
            },
          },
        },
        MuiButton: {
          styleOverrides: {
            root: {
              textTransform: 'none',
              fontWeight: 500,
              borderRadius: '8px',
              transition: 'all 0.2s ease-in-out',
            },
          },
        },
        MuiPaper: {
          styleOverrides: {
            root: {
              transition: 'background-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
              backgroundImage: 'none',
            },
          },
        },
        MuiCard: {
          styleOverrides: {
            root: {
              transition: 'all 0.3s ease-in-out',
            },
          },
        },
      },
    });
  }, []);

  // Preview a theme temporarily
  const previewThemeById = useCallback(async (themeId: string) => {
    try {
      setIsApplying(true);
      const themeData = await fetchThemeDetails(themeId);
      const muiTheme = createMUITheme(themeData, themeContext.isDark);
      setPreviewTheme(muiTheme);
      setAppliedTheme(themeId);
      
      // Store the preview in localStorage for persistence
      localStorage.setItem('preview-theme', themeId);
      
      console.log(`Previewing theme: ${themeData.display_name}`);
    } catch (error) {
      console.error('Failed to preview theme:', error);
    } finally {
      setIsApplying(false);
    }
  }, [fetchThemeDetails, createMUITheme, themeContext.isDark]);

  // Apply a theme permanently
  const applyTheme = useCallback(async (themeId: string) => {
    try {
      setIsApplying(true);
      const themeData = await fetchThemeDetails(themeId);
      const muiTheme = createMUITheme(themeData, themeContext.isDark);
      setPreviewTheme(muiTheme);
      setAppliedTheme(themeId);
      
      // Store the applied theme in localStorage
      localStorage.setItem('applied-theme', themeId);
      localStorage.removeItem('preview-theme');
      
      console.log(`Applied theme: ${themeData.display_name}`);
    } catch (error) {
      console.error('Failed to apply theme:', error);
    } finally {
      setIsApplying(false);
    }
  }, [fetchThemeDetails, createMUITheme, themeContext.isDark]);

  // Clear preview and revert to default
  const clearPreview = useCallback(() => {
    setPreviewTheme(null);
    setAppliedTheme(null);
    localStorage.removeItem('preview-theme');
    console.log('Cleared theme preview');
  }, []);

  // Load saved theme on initialization
  const loadSavedTheme = useCallback(async () => {
    const appliedThemeId = localStorage.getItem('applied-theme');
    const previewThemeId = localStorage.getItem('preview-theme');
    
    const themeToLoad = previewThemeId || appliedThemeId;
    if (themeToLoad) {
      try {
        const themeData = await fetchThemeDetails(themeToLoad);
        const muiTheme = createMUITheme(themeData, themeContext.isDark);
        setPreviewTheme(muiTheme);
        setAppliedTheme(themeToLoad);
      } catch (error) {
        console.error('Failed to load saved theme:', error);
        // Clear invalid theme from storage
        localStorage.removeItem('applied-theme');
        localStorage.removeItem('preview-theme');
      }
    }
  }, [fetchThemeDetails, createMUITheme, themeContext.isDark]);

  return {
    isApplying,
    appliedTheme,
    previewTheme,
    previewThemeById,
    applyTheme,
    clearPreview,
    loadSavedTheme,
  };
};
