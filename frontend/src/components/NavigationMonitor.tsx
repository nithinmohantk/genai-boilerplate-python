import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

interface NavigationMonitorProps {
  children: React.ReactNode;
}

/**
 * NavigationMonitor component that watches for route changes and forces
 * re-renders when navigation occurs. This helps fix navigation issues
 * caused by complex provider nesting.
 */
const NavigationMonitor: React.FC<NavigationMonitorProps> = ({ children }) => {
  const location = useLocation();
  const [forceUpdate, setForceUpdate] = React.useState(0);

  useEffect(() => {
    console.log('🎯 NavigationMonitor: Route changed to:', location.pathname);
    console.log('🎯 NavigationMonitor: Full location object:', location);
    
    // Force a re-render by updating state
    setForceUpdate(prev => prev + 1);
    
    // Dispatch a custom event for any components that might need it
    window.dispatchEvent(new CustomEvent('navigation-change', {
      detail: { 
        pathname: location.pathname,
        search: location.search,
        hash: location.hash,
        timestamp: Date.now()
      }
    }));
    
  }, [location]);

  // Use the location pathname as a key to force remounting of children
  return (
    <div key={`${location.pathname}-${forceUpdate}`}>
      {children}
    </div>
  );
};

export default NavigationMonitor;
