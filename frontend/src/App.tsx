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

// Routes component that forces re-render on location change
function AppRoutes() {
  const location = useLocation();
  console.log('🔄 AppRoutes: Location changed, re-rendering routes for:', location.pathname);
  
  return (
    <Routes key={location.pathname}>
      <Route path="/" element={<ChatPage key="chat-home" />} />
      <Route path="/chat" element={<ChatPage key="chat" />} />
      <Route path="/documents" element={<DocumentsPage key="documents" />} />
      <Route path="/settings" element={<SettingsPage key="settings" />} />
      <Route path="/admin" element={<AdminPage key="admin" />} />
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
