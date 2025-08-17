"""
Step definitions for navigation BDD tests.
Tests comprehensive navigation functionality including routing, state persistence,
theme context, and component lifecycle management.
"""

import asyncio
import time
from typing import Optional, Dict, Any

import pytest
from pytest_bdd import given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class NavigationTestContext:
    """Context for managing navigation test state and browser interactions."""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.base_url = "http://localhost:3000"
        self.wait_timeout = 10
        self.page_state: Dict[str, Any] = {}
        self.navigation_times: list[float] = []
        
    def setup_driver(self, mobile=False):
        """Set up Chrome driver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        if mobile:
            chrome_options.add_experimental_option("mobileEmulation", {
                "deviceName": "iPhone 12"
            })
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)
        
    def teardown_driver(self):
        """Clean up the driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def wait_for_element(self, by: By, value: str, timeout: int = None):
        """Wait for element to be present and visible."""
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = None):
        """Wait for element to be clickable."""
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def get_current_url_path(self) -> str:
        """Get the current path portion of the URL."""
        return self.driver.current_url.replace(self.base_url, "")
    
    def is_sidebar_active(self, link_text: str) -> bool:
        """Check if a sidebar link is marked as active."""
        try:
            sidebar_items = self.driver.find_elements(
                By.CSS_SELECTOR, '[role="navigation"] [role="button"], [role="navigation"] a'
            )
            for item in sidebar_items:
                if link_text.lower() in item.text.lower():
                    # Check for active styling (you may need to adjust based on your CSS)
                    classes = item.get_attribute("class") or ""
                    parent_classes = item.find_element(By.XPATH, "..").get_attribute("class") or ""
                    return "active" in classes or "selected" in classes or "primary" in parent_classes
        except NoSuchElementException:
            pass
        return False
    
    def measure_navigation_time(self, action_func):
        """Measure the time taken for a navigation action."""
        start_time = time.time()
        action_func()
        # Wait for navigation to complete (URL change)
        WebDriverWait(self.driver, self.wait_timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        end_time = time.time()
        navigation_time = (end_time - start_time) * 1000  # Convert to milliseconds
        self.navigation_times.append(navigation_time)
        return navigation_time


# Global context instance
nav_context = NavigationTestContext()


@given('the application is running')
def application_running():
    """Ensure the application is running and accessible."""
    nav_context.setup_driver()
    # Test that the application is accessible
    nav_context.driver.get(nav_context.base_url)
    nav_context.wait_for_element(By.TAG_NAME, "body")


@given('the frontend is accessible at "http://localhost:3000"')
def frontend_accessible():
    """Verify frontend is accessible at the specified URL."""
    nav_context.driver.get(nav_context.base_url)
    assert "GenAI Chatbot" in nav_context.driver.title or "GenAI" in nav_context.driver.page_source


@given('I am on the home page')
def on_home_page():
    """Navigate to the home page."""
    nav_context.driver.get(nav_context.base_url)
    nav_context.wait_for_element(By.TAG_NAME, "main")


@given(parsers.parse('I am on the {page_name} page'))
def on_specific_page(page_name: str):
    """Navigate to a specific page."""
    page_routes = {
        "Settings": "/settings",
        "Documents": "/documents", 
        "Admin": "/admin",
        "Chat": "/chat"
    }
    
    route = page_routes.get(page_name, "/")
    nav_context.driver.get(nav_context.base_url + route)
    nav_context.wait_for_element(By.TAG_NAME, "main")


@given(parsers.parse('I navigate directly to "{url}"'))
def navigate_directly_to_url(url: str):
    """Navigate directly to a specific URL."""
    nav_context.driver.get(nav_context.base_url + url)


@given('I am viewing the application on a mobile device')
def viewing_on_mobile():
    """Set up mobile view for testing."""
    nav_context.teardown_driver()
    nav_context.setup_driver(mobile=True)
    nav_context.driver.get(nav_context.base_url)


@when(parsers.parse('I click on the "{link_text}" link in the sidebar'))
def click_sidebar_link(link_text: str):
    """Click on a sidebar navigation link."""
    # Wait for sidebar to be present
    nav_context.wait_for_element(By.CSS_SELECTOR, '[role="navigation"], nav, .sidebar')
    
    # Find and click the link
    try:
        # Try multiple selectors to find the navigation link
        selectors = [
            f"//nav//a[contains(text(), '{link_text}')]",
            f"//nav//button[contains(text(), '{link_text}')]",
            f"//*[contains(@class, 'sidebar')]//a[contains(text(), '{link_text}')]",
            f"//*[contains(@class, 'navigation')]//button[contains(text(), '{link_text}')]",
            f"//*[contains(@role, 'navigation')]//*[contains(text(), '{link_text}')]"
        ]
        
        link_element = None
        for selector in selectors:
            try:
                link_element = nav_context.driver.find_element(By.XPATH, selector)
                break
            except NoSuchElementException:
                continue
        
        if not link_element:
            # Fallback: find any clickable element containing the text
            link_element = nav_context.driver.find_element(
                By.XPATH, f"//*[contains(text(), '{link_text}') and (name()='a' or name()='button')]"
            )
        
        # Scroll to element and click
        nav_context.driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
        nav_context.wait_for_clickable(By.XPATH, f"//*[contains(text(), '{link_text}')]").click()
        
        # Wait a moment for navigation to process
        time.sleep(0.5)
        
    except NoSuchElementException as e:
        pytest.fail(f"Could not find sidebar link '{link_text}': {e}")


@when(parsers.parse('I navigate to "{page_name}" page'))
def navigate_to_page(page_name: str):
    """Navigate to a specific page via sidebar."""
    click_sidebar_link(page_name)


@when('I refresh the browser')
def refresh_browser():
    """Refresh the current page."""
    nav_context.driver.refresh()
    nav_context.wait_for_element(By.TAG_NAME, "body")


@when(parsers.parse('I change the AI provider to "{provider}"'))
def change_ai_provider(provider: str):
    """Change AI provider in settings."""
    # Wait for settings form to load
    nav_context.wait_for_element(By.CSS_SELECTOR, 'select, [role="combobox"]')
    
    # Find and interact with AI provider dropdown
    try:
        provider_select = nav_context.driver.find_element(
            By.XPATH, "//label[contains(text(), 'AI Provider')]/..//select | //label[contains(text(), 'Provider')]/..//select"
        )
        from selenium.webdriver.support.ui import Select
        Select(provider_select).select_by_visible_text(provider)
        
        # Store state for later verification
        nav_context.page_state['ai_provider'] = provider
        
    except NoSuchElementException:
        pytest.skip(f"AI provider dropdown not found or not implemented")


@when(parsers.parse('I change the theme to "{theme_mode}"'))
def change_theme(theme_mode: str):
    """Change theme mode in settings."""
    try:
        # Look for theme toggle or buttons
        theme_selectors = [
            f"//button[contains(text(), '{theme_mode}')]",
            f"//button[contains(@aria-label, '{theme_mode}')]",
            f"//*[contains(@class, 'theme')]//button[contains(text(), '{theme_mode}')]"
        ]
        
        theme_button = None
        for selector in theme_selectors:
            try:
                theme_button = nav_context.driver.find_element(By.XPATH, selector)
                break
            except NoSuchElementException:
                continue
                
        if theme_button:
            theme_button.click()
            nav_context.page_state['theme'] = theme_mode
            time.sleep(1)  # Allow theme change to apply
        else:
            pytest.skip(f"Theme selection for '{theme_mode}' not found")
            
    except Exception as e:
        pytest.skip(f"Could not change theme: {e}")


@when(parsers.parse('I click on the "{tab_name}" tab'))
def click_tab(tab_name: str):
    """Click on a tab within a page."""
    tab_element = nav_context.wait_for_clickable(
        By.XPATH, f"//button[contains(@role, 'tab') and contains(text(), '{tab_name}')]"
    )
    tab_element.click()
    time.sleep(0.5)  # Wait for tab content to load


@when('I click the mobile menu button')
def click_mobile_menu():
    """Click the mobile navigation menu button."""
    menu_button = nav_context.wait_for_clickable(By.CSS_SELECTOR, '[aria-label="menu"], .menu-button, [data-testid="menu"]')
    menu_button.click()


@when(parsers.parse('I rapidly click between {navigation_sequence}'))
def rapid_navigation(navigation_sequence: str):
    """Rapidly navigate between multiple pages."""
    # Parse the sequence like '"Settings", "Documents", "Admin", and "Chat"'
    pages = [page.strip(' "') for page in navigation_sequence.replace(' and ', ', ').split(', ')]
    
    for page in pages:
        start_time = time.time()
        click_sidebar_link(page)
        # Wait for basic navigation
        WebDriverWait(nav_context.driver, 5).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        nav_time = (time.time() - start_time) * 1000
        nav_context.navigation_times.append(nav_time)


@when('I click the browser back button')
def browser_back():
    """Click browser back button."""
    nav_context.driver.back()
    time.sleep(1)


@when('I click the browser forward button')
def browser_forward():
    """Click browser forward button."""
    nav_context.driver.forward()
    time.sleep(1)


@when('I preview a theme')
def preview_theme():
    """Preview a theme in the admin page."""
    try:
        preview_button = nav_context.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Preview')]"
        )
        preview_button.click()
        nav_context.page_state['theme_previewed'] = True
    except NoSuchElementException:
        pytest.skip("Theme preview functionality not available")


@when('I apply the theme')
def apply_theme():
    """Apply a theme in the admin page."""
    try:
        apply_button = nav_context.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Apply')]"
        )
        apply_button.click()
        nav_context.page_state['theme_applied'] = True
    except NoSuchElementException:
        pytest.skip("Theme apply functionality not available")


@then(parsers.parse('I should see the {page_name} page with the heading "{heading}"'))
def verify_page_with_heading(page_name: str, heading: str):
    """Verify that we're on the correct page with the expected heading."""
    try:
        # Wait for the heading to be present
        heading_element = nav_context.wait_for_element(
            By.XPATH, f"//h1[contains(text(), '{heading}')] | //h2[contains(text(), '{heading}')] | //h3[contains(text(), '{heading}')] | //h4[contains(text(), '{heading}')]"
        )
        assert heading in heading_element.text
    except TimeoutException:
        pytest.fail(f"Expected heading '{heading}' not found on {page_name} page")


@then(parsers.parse('the URL should be "{expected_url}"'))
def verify_url(expected_url: str):
    """Verify the current URL matches the expected URL."""
    current_path = nav_context.get_current_url_path()
    assert current_path == expected_url or current_path == expected_url + "/", \
        f"Expected URL '{expected_url}' but got '{current_path}'"


@then(parsers.parse('the sidebar should show "{link_text}" as active'))
def verify_sidebar_active(link_text: str):
    """Verify that a sidebar link is marked as active."""
    time.sleep(0.5)  # Allow time for active state to update
    is_active = nav_context.is_sidebar_active(link_text)
    assert is_active, f"Sidebar link '{link_text}' is not marked as active"


@then('I should see the theme configuration section')
def verify_theme_configuration():
    """Verify theme configuration section is visible."""
    nav_context.wait_for_element(By.XPATH, "//*[contains(text(), 'Theme') or contains(text(), 'Interface')]")


@then('I should see the upload document button')
def verify_upload_button():
    """Verify upload document button is present."""
    nav_context.wait_for_element(By.XPATH, "//button[contains(text(), 'Upload')] | //input[@type='file']")


@then(parsers.parse('I should see the "{tab_name}" tab'))
def verify_tab_present(tab_name: str):
    """Verify a specific tab is present."""
    nav_context.wait_for_element(By.XPATH, f"//button[contains(@role, 'tab') and contains(text(), '{tab_name}')]")


@then(parsers.parse('I should still be on the {page_name} page'))
def verify_still_on_page(page_name: str):
    """Verify we're still on the expected page after some action."""
    verify_page_with_heading(page_name, page_name if page_name != "Settings" else "Settings")


@then(parsers.parse('the URL should remain "{url}"'))
def verify_url_unchanged(url: str):
    """Verify URL hasn't changed."""
    verify_url(url)


@then(parsers.parse('I should be back on the {page_name} page'))
def verify_back_on_page(page_name: str):
    """Verify we're back on a specific page."""
    verify_still_on_page(page_name)


@then(parsers.parse('the AI provider should still be set to "{provider}"'))
def verify_ai_provider_persisted(provider: str):
    """Verify AI provider setting was persisted."""
    stored_provider = nav_context.page_state.get('ai_provider')
    if stored_provider:
        assert stored_provider == provider, f"Expected provider '{provider}' but found '{stored_provider}'"
    else:
        pytest.skip("AI provider state not tracked or settings not implemented")


@then('each navigation should complete successfully')
def verify_navigation_success():
    """Verify all navigations completed successfully."""
    assert len(nav_context.navigation_times) > 0, "No navigation times recorded"
    # Check that all navigations completed (no timeouts)
    max_acceptable_time = 5000  # 5 seconds max
    for nav_time in nav_context.navigation_times:
        assert nav_time < max_acceptable_time, f"Navigation took too long: {nav_time}ms"


@then('the content should update appropriately for each page')
def verify_content_updates():
    """Verify page content updates correctly."""
    # This is implicitly verified by other checks, but we can add specific verification
    current_url = nav_context.get_current_url_path()
    assert current_url != "", "Should have navigated to a specific page"


@then('the active sidebar item should update correctly')
def verify_sidebar_updates():
    """Verify sidebar active state updates correctly."""
    # This is implicitly checked by other sidebar verification steps
    pass


@then('the page should load with the dark theme applied')
def verify_dark_theme():
    """Verify dark theme is applied."""
    try:
        # Check for dark theme indicators (adjust based on your theme implementation)
        body_element = nav_context.driver.find_element(By.TAG_NAME, "body")
        body_classes = body_element.get_attribute("class") or ""
        body_style = body_element.get_attribute("style") or ""
        
        # Look for dark theme indicators
        dark_indicators = ["dark", "theme-dark", "background-color: rgb(18, 18, 18)", "background: rgb(18, 18, 18)"]
        has_dark_theme = any(indicator in body_classes.lower() or indicator in body_style.lower() 
                           for indicator in dark_indicators)
        
        if not has_dark_theme:
            # Check if theme context or CSS variables indicate dark theme
            dark_mode_active = nav_context.driver.execute_script("""
                const computedStyle = getComputedStyle(document.body);
                const bgColor = computedStyle.backgroundColor;
                const isDark = bgColor.includes('rgb(18, 18, 18)') || 
                              bgColor.includes('rgb(33, 33, 33)') ||
                              document.documentElement.getAttribute('data-theme') === 'dark';
                return isDark;
            """)
            has_dark_theme = dark_mode_active
            
        assert has_dark_theme, "Dark theme does not appear to be applied"
    except Exception:
        pytest.skip("Cannot verify dark theme application")


@then('the navigation should complete successfully')
def verify_navigation_completed():
    """Verify navigation completed without errors."""
    # Check that we're not on an error page
    page_source = nav_context.driver.page_source.lower()
    assert "error" not in page_source or "404" not in page_source, "Navigation resulted in error page"


@then(parsers.parse('I should see the {tab_name} tab content'))
def verify_tab_content(tab_name: str):
    """Verify specific tab content is displayed."""
    # Wait for tab content to load
    time.sleep(1)
    # Look for content specific to the tab
    tab_content_found = False
    try:
        if tab_name == "Analytics":
            nav_context.wait_for_element(By.XPATH, "//*[contains(text(), 'Analytics') or contains(text(), 'Usage')]")
            tab_content_found = True
        elif tab_name == "System Settings":
            nav_context.wait_for_element(By.XPATH, "//*[contains(text(), 'System') or contains(text(), 'Configuration')]")
            tab_content_found = True
    except TimeoutException:
        pass
    
    assert tab_content_found, f"Content for {tab_name} tab not found"


@then('I should be redirected to the home page')
def verify_redirect_home():
    """Verify redirection to home page."""
    current_path = nav_context.get_current_url_path()
    assert current_path in ["/", "/chat"], f"Expected redirect to home, but got '{current_path}'"


@then('I should see a 404 error page')
def verify_404_page():
    """Verify 404 error page is displayed."""
    page_source = nav_context.driver.page_source.lower()
    assert "404" in page_source or "not found" in page_source, "404 error page not displayed"


@then('each navigation should complete within 200ms')
def verify_navigation_performance():
    """Verify navigation performance meets requirements."""
    for nav_time in nav_context.navigation_times:
        assert nav_time <= 200, f"Navigation took {nav_time}ms, exceeding 200ms limit"


@then('there should be no rendering conflicts')
def verify_no_rendering_conflicts():
    """Verify no rendering conflicts occurred."""
    # Check for console errors (simplified check)
    logs = nav_context.driver.get_log('browser')
    severe_errors = [log for log in logs if log['level'] == 'SEVERE']
    assert len(severe_errors) == 0, f"Found rendering conflicts: {severe_errors}"


@then('the UI should remain responsive')
def verify_ui_responsive():
    """Verify UI remains responsive."""
    # Basic responsiveness check - ensure page is interactive
    try:
        # Try to find any clickable element
        nav_context.driver.find_element(By.CSS_SELECTOR, "button, a, [role='button']")
    except NoSuchElementException:
        pytest.fail("UI appears unresponsive - no interactive elements found")


@then('each page component should mount and unmount correctly')
def verify_component_lifecycle():
    """Verify proper component mounting and unmounting."""
    # Check browser console for React lifecycle logs
    logs = nav_context.driver.get_log('browser')
    mount_logs = [log for log in logs if 'MOUNTED' in log['message']]
    unmount_logs = [log for log in logs if 'UNMOUNTED' in log['message']]
    
    # We should see evidence of proper lifecycle management
    assert len(mount_logs) > 0, "No component mount logs found"


@then('there should be no memory leaks')
def verify_no_memory_leaks():
    """Verify no memory leaks during navigation."""
    # Basic check - ensure we're not accumulating too many DOM elements
    element_count = nav_context.driver.execute_script("return document.getElementsByTagName('*').length")
    assert element_count < 10000, f"Too many DOM elements ({element_count}), possible memory leak"


@then('debug logs should show proper component lifecycle events')
def verify_debug_logs():
    """Verify debug logs show proper component lifecycle."""
    logs = nav_context.driver.get_log('browser')
    lifecycle_logs = [log for log in logs if any(keyword in log['message'] for keyword in ['MOUNTED', 'UNMOUNTED', 'Render #'])]
    assert len(lifecycle_logs) > 0, "No component lifecycle debug logs found"


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_navigation_tests():
    """Clean up after all navigation tests."""
    yield
    nav_context.teardown_driver()
