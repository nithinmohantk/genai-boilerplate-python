import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface NavigationMonitorProps {
  children: React.ReactNode;
}

/**
 * Enhanced NavigationMonitor component that forcefully handles route changes
 * and ensures content remounting. This fixes navigation issues by manually
 * triggering re-renders and DOM reflows. Works in conjunction with Layout's
 * sidebar refresh mechanism.
 */
const NavigationMonitor: React.FC<NavigationMonitorProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [forceUpdate, setForceUpdate] = React.useState(0);
  const [isTransitioning, setIsTransitioning] = React.useState(false);
  const previousPathRef = useRef<string>(location.pathname);
  const contentRef = useRef<HTMLDivElement>(null);
  const transitionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Enhanced navigation monitoring with transition management
  useEffect(() => {
    // Only proceed if the path has actually changed
    if (previousPathRef.current === location.pathname) {
      return;
    }
    
    console.log('🎯 NavigationMonitor: Route changed from', previousPathRef.current, 'to:', location.pathname);
    
    // Clear any existing transition timeout
    if (transitionTimeoutRef.current) {
      clearTimeout(transitionTimeoutRef.current);
    }
    
    // Start transition state
    setIsTransitioning(true);
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
    
    // Dispatch enhanced navigation event with transition info
    window.dispatchEvent(new CustomEvent('navigation-change', {
      detail: { 
        pathname: location.pathname,
        search: location.search,
        hash: location.hash,
        previousPath: previousPathRef.current,
        timestamp: Date.now(),
        isTransitioning: true
      }
    }));
    
    // End transition after content has time to load
    transitionTimeoutRef.current = setTimeout(() => {
      setIsTransitioning(false);
      
      // Dispatch transition complete event
      window.dispatchEvent(new CustomEvent('navigation-transition-complete', {
        detail: { 
          pathname: location.pathname,
          timestamp: Date.now()
        }
      }));
      
      console.log('✅ NavigationMonitor: Transition complete for:', location.pathname);
    }, 200);
    
    // Set up a backup timer to force re-navigate if content doesn't update
    const backupTimer = setTimeout(() => {
      // If we still see issues, force a hard reload of the route
      const currentPath = window.location.pathname;
      if (currentPath === location.pathname && isTransitioning) {
        console.log('🔄 NavigationMonitor: Forcing route refresh for:', location.pathname);
        // Re-navigate to the same route to force a full refresh
        navigate(location.pathname, { replace: true, state: { forceRefresh: Date.now() } });
      }
    }, 1000); // Longer timeout for backup
    
    return () => {
      if (transitionTimeoutRef.current) {
        clearTimeout(transitionTimeoutRef.current);
      }
      clearTimeout(backupTimer);
    };
  }, [location, navigate, isTransitioning]);

  // Use a combination of key-based remounting and ref-based DOM manipulation with transition state
  return (
    <div 
      ref={contentRef}
      key={`route-${location.pathname}-${forceUpdate}`}
      data-current-route={location.pathname}
      data-route-timestamp={Date.now()}
      data-is-transitioning={isTransitioning}
      style={{
        transition: 'opacity 0.2s ease',
        opacity: isTransitioning ? 0.8 : 1,
      }}
    >
      {children}
    </div>
  );
};

export default NavigationMonitor;
