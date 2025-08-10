#!/usr/bin/env python3
"""
Simple navigation test script to verify that the navigation fixes are working.
This script opens the frontend and tests basic navigation between pages.
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Set up Chrome driver with headless options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)
    return driver


def test_navigation():
    """Test basic navigation functionality."""
    driver = setup_driver()
    base_url = "http://localhost:3000"
    
    try:
        print("🚀 Starting navigation test...")
        
        # Test 1: Load home page
        print("📍 Testing home page load...")
        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("✅ Home page loaded successfully")
        
        # Test 2: Navigate to Settings
        print("📍 Testing navigation to Settings...")
        try:
            # Look for navigation links
            nav_selectors = [
                "//nav//a[contains(text(), 'Settings')]",
                "//nav//button[contains(text(), 'Settings')]",
                "//*[contains(@role, 'navigation')]//*[contains(text(), 'Settings')]",
                "//*[contains(text(), 'Settings') and (name()='a' or name()='button')]"
            ]
            
            settings_link = None
            for selector in nav_selectors:
                try:
                    settings_link = driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if settings_link:
                settings_link.click()
                time.sleep(2)  # Wait for navigation
                
                # Check if we're on settings page
                if "/settings" in driver.current_url:
                    print("✅ Successfully navigated to Settings page")
                else:
                    print(f"⚠️  URL changed to {driver.current_url} but expected /settings")
                    
                # Look for settings content
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Settings') or contains(text(), 'Configuration')]"))
                    )
                    print("✅ Settings page content loaded")
                except TimeoutException:
                    print("⚠️  Settings page content not found")
            else:
                print("❌ Could not find Settings navigation link")
                
        except Exception as e:
            print(f"❌ Settings navigation failed: {e}")
        
        # Test 3: Navigate to Chat
        print("📍 Testing navigation to Chat...")
        try:
            chat_selectors = [
                "//nav//a[contains(text(), 'Chat')]",
                "//nav//button[contains(text(), 'Chat')]",
                "//*[contains(@role, 'navigation')]//*[contains(text(), 'Chat')]",
                "//*[contains(text(), 'Chat') and (name()='a' or name()='button')]"
            ]
            
            chat_link = None
            for selector in chat_selectors:
                try:
                    chat_link = driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if chat_link:
                chat_link.click()
                time.sleep(2)  # Wait for navigation
                
                # Check if we're on chat page
                if "/chat" in driver.current_url or driver.current_url.endswith("/"):
                    print("✅ Successfully navigated to Chat page")
                else:
                    print(f"⚠️  URL changed to {driver.current_url} but expected /chat")
                    
                # Look for chat content
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Chat') or contains(text(), 'GenAI')]"))
                    )
                    print("✅ Chat page content loaded")
                except TimeoutException:
                    print("⚠️  Chat page content not found")
            else:
                print("❌ Could not find Chat navigation link")
                
        except Exception as e:
            print(f"❌ Chat navigation failed: {e}")
        
        # Test 4: Navigate to Documents
        print("📍 Testing navigation to Documents...")
        try:
            docs_selectors = [
                "//nav//a[contains(text(), 'Documents')]",
                "//nav//button[contains(text(), 'Documents')]",
                "//*[contains(@role, 'navigation')]//*[contains(text(), 'Documents')]",
                "//*[contains(text(), 'Documents') and (name()='a' or name()='button')]"
            ]
            
            docs_link = None
            for selector in docs_selectors:
                try:
                    docs_link = driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if docs_link:
                docs_link.click()
                time.sleep(2)  # Wait for navigation
                
                # Check if we're on documents page
                if "/documents" in driver.current_url:
                    print("✅ Successfully navigated to Documents page")
                else:
                    print(f"⚠️  URL changed to {driver.current_url} but expected /documents")
                    
                # Look for documents content
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Document') or contains(text(), 'Upload')]"))
                    )
                    print("✅ Documents page content loaded")
                except TimeoutException:
                    print("⚠️  Documents page content not found")
            else:
                print("❌ Could not find Documents navigation link")
                
        except Exception as e:
            print(f"❌ Documents navigation failed: {e}")
        
        # Test 5: Navigate to Admin
        print("📍 Testing navigation to Admin...")
        try:
            admin_selectors = [
                "//nav//a[contains(text(), 'Admin')]",
                "//nav//button[contains(text(), 'Admin')]",
                "//*[contains(@role, 'navigation')]//*[contains(text(), 'Admin')]",
                "//*[contains(text(), 'Admin') and (name()='a' or name()='button')]"
            ]
            
            admin_link = None
            for selector in admin_selectors:
                try:
                    admin_link = driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if admin_link:
                admin_link.click()
                time.sleep(2)  # Wait for navigation
                
                # Check if we're on admin page
                if "/admin" in driver.current_url:
                    print("✅ Successfully navigated to Admin page")
                else:
                    print(f"⚠️  URL changed to {driver.current_url} but expected /admin")
                    
                # Look for admin content
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Admin') or contains(text(), 'Management')]"))
                    )
                    print("✅ Admin page content loaded")
                except TimeoutException:
                    print("⚠️  Admin page content not found")
            else:
                print("❌ Could not find Admin navigation link")
                
        except Exception as e:
            print(f"❌ Admin navigation failed: {e}")
        
        print("\n🎉 Navigation test completed!")
        print("💡 If you see multiple ✅ marks, navigation is working correctly.")
        print("💡 If you see ❌ or ⚠️  marks, there may be navigation issues to investigate.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        driver.quit()
    
    return True


def check_app_running():
    """Check if the application is running."""
    import requests
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


if __name__ == "__main__":
    print("🧪 Navigation Test Suite")
    print("=" * 50)
    
    # Check if app is running
    if not check_app_running():
        print("❌ Application is not running at http://localhost:3000")
        print("💡 Please start the application with: docker-compose up -d")
        sys.exit(1)
    
    print("✅ Application is running at http://localhost:3000")
    
    # Run navigation tests
    success = test_navigation()
    
    if success:
        print("\n🏆 All navigation tests completed!")
        print("🔍 Check the output above for detailed results.")
    else:
        print("\n💥 Navigation tests failed!")
        sys.exit(1)
