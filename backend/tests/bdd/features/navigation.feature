Feature: Application Navigation
  As a user
  I want to navigate between different pages in the application
  So that I can access all features efficiently

  Background:
    Given the application is running
    And the frontend is accessible at "http://localhost:3000"

  Scenario: Basic page navigation from sidebar
    Given I am on the home page
    When I click on the "Chat" link in the sidebar
    Then I should see the Chat page with the heading "GenAI Chat Assistant"
    And the URL should be "/chat"
    And the sidebar should show "Chat" as active

  Scenario: Navigate to Settings page
    Given I am on the home page
    When I click on the "Settings" link in the sidebar
    Then I should see the Settings page with the heading "Settings"
    And the URL should be "/settings"
    And the sidebar should show "Settings" as active
    And I should see the theme configuration section

  Scenario: Navigate to Documents page
    Given I am on the home page
    When I click on the "Documents" link in the sidebar
    Then I should see the Documents page with the heading "Document Management"
    And the URL should be "/documents"
    And the sidebar should show "Documents" as active
    And I should see the upload document button

  Scenario: Navigate to Admin page
    Given I am on the home page
    When I click on the "Admin" link in the sidebar
    Then I should see the Admin page with the heading "Admin Center"
    And the URL should be "/admin"
    And the sidebar should show "Admin" as active
    And I should see the "Theme Management" tab

  Scenario: Navigation persists after page refresh
    Given I am on the Settings page
    When I refresh the browser
    Then I should still be on the Settings page
    And the sidebar should show "Settings" as active
    And the URL should remain "/settings"

  Scenario: Direct URL navigation
    Given I navigate directly to "/documents"
    Then I should see the Documents page with the heading "Document Management"
    And the sidebar should show "Documents" as active

  Scenario: Navigation maintains component state
    Given I am on the Settings page
    When I change the AI provider to "Anthropic"
    And I click on the "Chat" link in the sidebar
    And I click on the "Settings" link in the sidebar
    Then I should be back on the Settings page
    And the AI provider should still be set to "Anthropic"

  Scenario: Sequential navigation between all pages
    Given I am on the home page
    When I navigate to "Chat" page
    And I navigate to "Documents" page
    And I navigate to "Settings" page
    And I navigate to "Admin" page
    Then each navigation should complete successfully
    And the content should update appropriately for each page
    And the active sidebar item should update correctly

  Scenario: Navigation with theme changes
    Given I am on the Settings page
    When I change the theme to "dark"
    And I navigate to the "Chat" page
    Then the page should load with the dark theme applied
    And the navigation should complete successfully

  Scenario: Admin page tab navigation
    Given I am on the Admin page
    When I click on the "Analytics" tab
    Then I should see the Analytics tab content
    And the URL should remain "/admin"
    When I click on the "System Settings" tab
    Then I should see the System Settings tab content
    And the URL should remain "/admin"

  Scenario: Navigation error handling
    Given I navigate directly to "/invalid-route"
    Then I should be redirected to the home page
    Or I should see a 404 error page

  Scenario: Responsive navigation on mobile
    Given I am viewing the application on a mobile device
    When I click the mobile menu button
    Then the navigation menu should expand
    When I click on "Settings" in the mobile menu
    Then I should navigate to the Settings page
    And the mobile menu should close

  Scenario: Keyboard navigation
    Given I am on the home page
    When I press Tab to focus on navigation
    And I use arrow keys to navigate
    And I press Enter on "Documents"
    Then I should navigate to the Documents page

  Scenario: Navigation performance
    Given I am on the Chat page
    When I rapidly click between "Settings", "Documents", "Admin", and "Chat"
    Then each navigation should complete within 200ms
    And there should be no rendering conflicts
    And the UI should remain responsive

  Scenario: Deep linking with query parameters
    Given I navigate directly to "/admin?tab=analytics"
    Then I should be on the Admin page
    And the Analytics tab should be active

  Scenario: Browser back and forward navigation
    Given I am on the home page
    When I navigate to "Settings"
    And I navigate to "Documents"
    And I click the browser back button
    Then I should be on the Settings page
    When I click the browser forward button
    Then I should be on the Documents page

  Scenario: Navigation component re-rendering
    Given I am on any page
    When I navigate between different pages multiple times
    Then each page component should mount and unmount correctly
    And there should be no memory leaks
    And debug logs should show proper component lifecycle events

  Scenario: Navigation with theme application context
    Given I am on the Admin page
    When I preview a theme
    And I navigate to another page
    Then the previewed theme should persist across navigation
    When I apply the theme
    And I navigate between pages
    Then the applied theme should remain consistent

  Scenario: Navigation during loading states
    Given I am on a page with loading content
    When I navigate to another page before loading completes
    Then the navigation should interrupt the loading
    And the new page should load correctly
    And there should be no hanging requests

  Scenario: Navigation state persistence in theme context
    Given I have the advanced theme system enabled
    When I navigate between pages
    Then theme context should persist
    And theme preview states should be maintained
    And applied themes should remain active
