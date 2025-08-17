import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CssBaseline from '@mui/material/CssBaseline';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import SettingsPage from './pages/SettingsPage';
import AdminPage from './pages/AdminPage';
import { globalThemeManager } from './utils/globalThemeManager';
import { CustomThemeProvider } from './contexts/ThemeContext';
import { ThemeApplicationProvider } from './contexts/ThemeApplicationContext';

// Enhanced Routes component with forced re-rendering and component isolation
function AppRoutes() {
  const location = useLocation();
  const [routeKey, setRouteKey] = React.useState(0);
  
  // Force re-render whenever location changes
  React.useEffect(() => {
    console.log('🔄 AppRoutes: Location changed, forcing re-render for:', location.pathname);
    setRouteKey(prev => prev + 1);
    
    // Force a micro-task to ensure React has time to process the change
    setTimeout(() => {
      console.log('🔄 AppRoutes: Route key updated to:', routeKey + 1);
    }, 0);
  }, [location.pathname]);
  
  // Create unique keys for each component based on path and timestamp
  const getComponentKey = (baseName: string) => `${baseName}-${location.pathname}-${routeKey}`;
  
  return (
    <Routes key={`routes-${location.pathname}-${routeKey}`}>
      <Route 
        path="/" 
        element={<ChatPage key={getComponentKey('chat-home')} />} 
      />
      <Route 
        path="/chat" 
        element={<ChatPage key={getComponentKey('chat')} />} 
      />
      <Route 
        path="/documents" 
        element={<DocumentsPage key={getComponentKey('documents')} />} 
      />
      <Route 
        path="/settings" 
        element={<SettingsPage key={getComponentKey('settings')} />} 
      />
      <Route 
        path="/admin" 
        element={<AdminPage key={getComponentKey('admin')} />} 
      />
    </Routes>
  );
}

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  // Initialize the global theme manager
  React.useEffect(() => {
    globalThemeManager.init();
  }, []);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <CustomThemeProvider>
            <ThemeApplicationProvider>
              <CssBaseline />
              <Layout>
                <AppRoutes />
              </Layout>
            </ThemeApplicationProvider>
          </CustomThemeProvider>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
