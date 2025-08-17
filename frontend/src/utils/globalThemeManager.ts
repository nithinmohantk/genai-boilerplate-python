// Global theme manager to handle theme recreation when base mode changes
// This ensures we have a single source of truth for theme management

import { createTheme, type Theme } from '@mui/material/styles';

interface BackendTheme {
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

class ThemeManager {
  private currentThemeId: string | null = null;
  private currentThemeData: BackendTheme | null = null;
  private isInitialized = false;

  // Initialize the theme manager
  init() {
    if (this.isInitialized) return;
    
    // Load current theme from localStorage on startup
    this.loadCurrentTheme();
    
    // Listen for base mode changes
    window.addEventListener('base-theme-mode-change', this.handleBaseModeChange.bind(this) as EventListener);
    
    this.isInitialized = true;
    console.log('Global theme manager initialized');
  }

  private loadCurrentTheme() {
    const appliedThemeId = localStorage.getItem('applied-theme');
    const previewThemeId = localStorage.getItem('preview-theme');
    
    this.currentThemeId = previewThemeId || appliedThemeId;
    console.log('Loaded current theme ID:', this.currentThemeId);
  }

  // Set the current theme data when a theme is applied/previewed
  setCurrentTheme(themeId: string, themeData: BackendTheme) {
    this.currentThemeId = themeId;
    this.currentThemeData = themeData;
    console.log('Set current theme:', themeData.display_name);
  }

  // Clear the current theme
  clearCurrentTheme() {
    this.currentThemeId = null;
    this.currentThemeData = null;
    console.log('Cleared current theme');
  }

  // Handle base mode changes
  private async handleBaseModeChange(event: Event) {
    const customEvent = event as CustomEvent;
    const isDark = customEvent.detail.isDark;
    console.log(`Global theme manager: handling mode change to ${isDark ? 'dark' : 'light'}`);
    
    if (this.currentThemeId && this.currentThemeData) {
      try {
        const muiTheme = this.createMUITheme(this.currentThemeData, isDark);
        
        // Dispatch event to update the main theme provider
        window.dispatchEvent(new CustomEvent('backend-theme-change', {
          detail: { theme: muiTheme, themeId: this.currentThemeId }
        }));
        
        console.log(`Recreated ${this.currentThemeData.display_name} for ${isDark ? 'dark' : 'light'} mode`);
      } catch (error) {
        console.error('Failed to recreate theme:', error);
      }
    }
  }

  private createMUITheme(backendTheme: BackendTheme, isDark: boolean): Theme {
    const colorScheme = backendTheme.color_scheme;
    if (!colorScheme) {
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
  }
}

// Create and export a global instance
export const globalThemeManager = new ThemeManager();
