import React, { type ReactNode, useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Fade,
  CircularProgress,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Description as DocumentsIcon,
  Settings as SettingsIcon,
  AdminPanelSettings as AdminIcon,
  Menu as MenuIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import DarkModeToggle from './DarkModeToggle';
import NavigationMonitor from './NavigationMonitor';

interface LayoutProps {
  children: ReactNode;
}

const drawerWidth = 240;

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const previousLocationRef = useRef(location.pathname);
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Enhanced sidebar refresh mechanism during page transitions
  useEffect(() => {
    // Only trigger refresh if the route actually changed
    if (previousLocationRef.current === location.pathname) {
      return;
    }

    console.log('🔄 Layout: Refreshing sidebar for route change:', previousLocationRef.current, '->', location.pathname);
    
    // Clear any existing timeout
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }

    // Start refresh animation
    setIsRefreshing(true);
    
    // Update the previous location reference
    previousLocationRef.current = location.pathname;
    
    // Force sidebar refresh with a slight delay for visual feedback
    refreshTimeoutRef.current = setTimeout(() => {
      setSidebarRefreshKey(prev => prev + 1);
      
      // Stop refresh animation after a brief moment
      setTimeout(() => {
        setIsRefreshing(false);
      }, 300);
    }, 150);

    // Cleanup timeout on unmount
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [location.pathname]);

  // Debug navigation changes
  useEffect(() => {
    console.log('🧭 Navigation Debug: Location changed to:', location.pathname);
    console.log('🧭 Navigation Debug: Full location object:', location);
    console.log('🔄 Sidebar refresh key:', sidebarRefreshKey);
  }, [location, sidebarRefreshKey]);

  const menuItems = [
    { text: 'Chat', icon: <ChatIcon />, path: '/chat' },
    { text: 'Documents', icon: <DocumentsIcon />, path: '/documents' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
    { text: 'Admin', icon: <AdminIcon />, path: '/admin' },
  ];

  const handleNavigation = (path: string) => {
    console.log('🎯 Layout: Navigating to:', path);
    
    // Trigger immediate sidebar refresh for responsive UI
    setIsRefreshing(true);
    setSidebarRefreshKey(prev => prev + 1);
    
    // Navigate to the new path
    navigate(path);
    
    // Stop refresh animation after navigation
    setTimeout(() => {
      setIsRefreshing(false);
    }, 500);
  };

  // Manual refresh function for the sidebar
  const handleManualRefresh = () => {
    console.log('🔄 Layout: Manual sidebar refresh triggered');
    setIsRefreshing(true);
    setSidebarRefreshKey(prev => prev + 1);
    
    setTimeout(() => {
      setIsRefreshing(false);
    }, 600);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          bgcolor: 'background.paper',
          color: 'text.primary',
          boxShadow: 1,
        }}
      >
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              GenAI Chatbot
            </Typography>
            <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 1 }}>
              {/* Manual sidebar refresh button */}
              <IconButton
                onClick={handleManualRefresh}
                disabled={isRefreshing}
                title="Refresh Sidebar"
                sx={{ 
                  color: 'text.secondary',
                  '&:hover': { color: 'primary.main' },
                  transition: 'all 0.2s ease'
                }}
              >
                {isRefreshing ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <RefreshIcon sx={{ 
                    animation: isRefreshing ? 'spin 1s linear infinite' : 'none',
                    '@keyframes spin': {
                      '0%': { transform: 'rotate(0deg)' },
                      '100%': { transform: 'rotate(360deg)' },
                    },
                  }} />
                )}
              </IconButton>
              <DarkModeToggle />
            </Box>
          </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              bgcolor: 'background.paper',
              borderRight: 1,
              borderColor: 'divider',
              position: 'relative',
              overflow: 'hidden',
            },
          }}
          open
        >
          <Toolbar />
          
          {/* Sidebar refresh indicator */}
          {isRefreshing && (
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                bgcolor: 'rgba(0, 0, 0, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                backdropFilter: 'blur(2px)',
              }}
            >
              <CircularProgress color="primary" size={30} />
            </Box>
          )}
          
          {/* Enhanced sidebar list with refresh key */}
          <Fade in={!isRefreshing} timeout={300}>
            <List 
              key={`sidebar-list-${sidebarRefreshKey}`}
              sx={{ 
                mt: 1,
                transition: 'all 0.3s ease',
                opacity: isRefreshing ? 0.3 : 1,
              }}
            >
              {menuItems.map((item) => (
                <ListItem
                  key={`${item.text}-${sidebarRefreshKey}`}
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    cursor: 'pointer',
                    mx: 1,
                    borderRadius: 1,
                    bgcolor: location.pathname === item.path ? 'primary.light' : 'transparent',
                    transform: isRefreshing ? 'scale(0.98)' : 'scale(1)',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      bgcolor: 'action.hover',
                      transform: 'scale(1.02)',
                    },
                    // Add refresh animation
                    animation: isRefreshing ? 'pulse 0.6s ease-in-out' : 'none',
                    '@keyframes pulse': {
                      '0%': { opacity: 0.7, transform: 'scale(0.98)' },
                      '50%': { opacity: 1, transform: 'scale(1)' },
                      '100%': { opacity: 0.7, transform: 'scale(0.98)' },
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: location.pathname === item.path ? 'primary.main' : 'text.secondary',
                      transition: 'color 0.2s ease',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    sx={{
                      color: location.pathname === item.path ? 'primary.main' : 'text.primary',
                      transition: 'color 0.2s ease',
                    }}
                  />
                  
                  {/* Active route indicator */}
                  {location.pathname === item.path && (
                    <Box
                      sx={{
                        position: 'absolute',
                        right: 8,
                        width: 4,
                        height: 20,
                        bgcolor: 'primary.main',
                        borderRadius: 2,
                        animation: 'slideIn 0.3s ease',
                        '@keyframes slideIn': {
                          '0%': { width: 0, opacity: 0 },
                          '100%': { width: 4, opacity: 1 },
                        },
                      }}
                    />
                  )}
                </ListItem>
              ))}
            </List>
          </Fade>
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <Toolbar />
        <NavigationMonitor>
          {children}
        </NavigationMonitor>
      </Box>
    </Box>
  );
};

export default Layout;
