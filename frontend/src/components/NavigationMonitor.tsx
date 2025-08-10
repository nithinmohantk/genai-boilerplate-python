import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface NavigationMonitorProps {
  children: React.ReactNode;
}

/**
 * Enhanced NavigationMonitor component that forcefully handles route changes
 * and ensures content remounting. This fixes navigation issues by manually
 * triggering re-renders and DOM reflows.
 */
const NavigationMonitor: React.FC<NavigationMonitorProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [forceUpdate, setForceUpdate] = React.useState(0);
  const previousPathRef = useRef<string>(location.pathname);
  const contentRef = useRef<HTMLDivElement>(null);
  
  // Enhanced navigation monitoring with additional safeguards
  useEffect(() => {
    // Only proceed if the path has actually changed
    if (previousPathRef.current === location.pathname) {
      return;
    }
    
    console.log('🎯 NavigationMonitor: Route changed from', previousPathRef.current, 'to:', location.pathname);
    previousPathRef.current = location.pathname;
    
    // Force a re-render by updating state
    setForceUpdate(prev => prev + 1);
    
    // Trigger a browser reflow by directly manipulating the DOM
    if (contentRef.current) {
      // Force a reflow by reading and writing to the DOM
      void contentRef.current.offsetHeight;
      contentRef.current.style.display = 'none';
      // Force a reflow
      void contentRef.current.offsetHeight;
      contentRef.current.style.display = '';
    }
    
    // Dispatch a custom event for any components that need to react to navigation
    window.dispatchEvent(new CustomEvent('navigation-change', {
      detail: { 
        pathname: location.pathname,
        search: location.search,
        hash: location.hash,
        timestamp: Date.now()
      }
    }));
    
    // Set up a backup timer to force re-navigate if content doesn't update
    const timer = setTimeout(() => {
      // If we still see issues, force a hard reload of the route
      const currentPath = window.location.pathname;
      if (currentPath === location.pathname) {
        console.log('🔄 NavigationMonitor: Forcing route refresh for:', location.pathname);
        // Re-navigate to the same route to force a full refresh
        navigate(location.pathname, { replace: true, state: { forceRefresh: Date.now() } });
      }
    }, 100); // Short timeout to avoid unnecessary refreshes
    
    return () => clearTimeout(timer);
  }, [location, navigate]);

  // Use a combination of key-based remounting and ref-based DOM manipulation
  return (
    <div 
      ref={contentRef}
      key={`route-${location.pathname}-${forceUpdate}`}
      data-current-route={location.pathname}
      data-route-timestamp={Date.now()}
    >
      {children}
    </div>
  );
};

export default NavigationMonitor;
