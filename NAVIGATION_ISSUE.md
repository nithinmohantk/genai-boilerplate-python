# Issue: Left Navigation Not Working - UI Not Refreshing on Route Changes

## Problem Description
The left sidebar navigation in the React frontend is not properly refreshing the UI when navigation items are clicked. Users must manually refresh the browser to see content changes after clicking navigation links.

## Current Behavior
1. Click on navigation items in left sidebar (Chat, Documents, Settings, Admin)
2. URL changes correctly in browser address bar
3. **UI content does not update** - still shows previous page content
4. Manual browser refresh (F5/Ctrl+R) is required to see the new page content

## Expected Behavior
1. Click on navigation items
2. URL changes in browser address bar  
3. **UI content updates immediately** to show the new page
4. No manual browser refresh needed

## Technical Details

### Environment
- React 18 with TypeScript
- React Router v6 
- Material-UI (MUI) v5
- Docker containerized frontend
- nginx serving static files

### Navigation Implementation
- Located in: `frontend/src/components/Layout.tsx`
- Uses React Router's `useNavigate()` and `useLocation()` hooks
- Navigation items call `navigate(path)` on click

### Router Setup  
- Located in: `frontend/src/App.tsx`
- Uses `BrowserRouter` with nested `Routes` and `Route` components
- Routes are properly configured for each page

### Suspected Root Cause
The issue likely stems from complex provider nesting in `App.tsx`:
```jsx
<ErrorBoundary>
  <QueryClientProvider client={queryClient}>
    <Router>
      <CustomThemeProvider>
        <ThemeApplicationProvider>
          <CssBaseline />
          <Layout>
            <Routes>
              <Route path="/" element={<ChatPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/admin" element={<AdminPage />} />
            </Routes>
          </Layout>
        </ThemeApplicationProvider>
      </CustomThemeProvider>
    </Router>
  </QueryClientProvider>
</ErrorBoundary>
```

### Potential Issues
1. **Theme providers causing re-render blocking**: Complex theme context providers may be interfering with React Router's navigation updates
2. **Event listener conflicts**: Theme system uses custom event listeners that might conflict with navigation
3. **Component memoization**: Pages might be memoized/cached in a way that prevents updates
4. **Router context issues**: Complex provider nesting might be breaking React Router context propagation

## Steps to Reproduce
1. Start the application: `docker-compose up`
2. Navigate to `http://localhost:3000`
3. Click any navigation item in left sidebar
4. Observe that URL changes but UI content remains the same
5. Refresh browser manually to see content update

## Acceptance Criteria
- [ ] Clicking navigation items immediately updates UI content
- [ ] No browser refresh required for navigation
- [ ] URL and UI content stay synchronized
- [ ] All theme functionality continues to work
- [ ] Navigation works consistently across all pages (Chat, Documents, Settings, Admin)

## Priority: High
This is a critical UX issue that makes the application nearly unusable without manual page refreshes.
