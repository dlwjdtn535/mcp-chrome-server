import logging
import random
import time
import os
from typing import Optional, Dict, Any, Union

import keyring
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

def get_chrome_profile_path() -> str:
    """Get the user's Chrome profile path.
    
    Retrieves the Chrome profile path from environment variables.
    If not set, returns the default path based on the operating system.
    
    Returns:
        str: Path to Chrome user profile directory
        
    Raises:
        Exception: If the profile path cannot be found
    """
    # Check environment variable first
    profile_path = os.getenv('CHROME_PROFILE_PATH')
    if profile_path:
        return profile_path
        
    # Default profile paths by OS
    if os.name == 'nt':  # Windows
        profile_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
    elif os.name == 'posix':  # macOS
        profile_path = os.path.expanduser('~/Library/Application Support/Google/Chrome')
    else:  # Linux
        profile_path = os.path.expanduser('~/.config/google-chrome')
        
    if not os.path.exists(profile_path):
        raise Exception(f"Chrome profile path not found: {profile_path}")
        
    return profile_path

class CredentialManager:
    """Secure credential management system"""
    
    @staticmethod
    def save_credentials(site: str, username: str, password: str) -> bool:
        """Securely save credentials to system keychain
        
        Args:
            site: Website domain or service identifier
            username: User's username or email
            password: User's password
            
        Returns:
            bool: True if credentials were saved successfully
        """
        try:
            keyring.set_password(site, username, password)
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
            return False
    
    @staticmethod
    def get_credentials(site: str, username: str) -> Optional[str]:
        """Retrieve stored credentials from system keychain
        
        Args:
            site: Website domain or service identifier
            username: User's username or email
            
        Returns:
            Optional[str]: Retrieved password or None if not found
        """
        try:
            return keyring.get_password(site, username)
        except Exception as e:
            logger.error(f"Failed to get credentials: {str(e)}")
            return None

class HumanEmulator:
    """Tools for emulating human-like behavior"""
    
    @staticmethod
    def get_random_delay() -> float:
        """Generate random delay to simulate human typing patterns
        
        Returns:
            float: Random delay between 0.1 and 0.3 seconds
        """
        return random.uniform(0.1, 0.3)
    
    @staticmethod
    def simulate_typing(element: WebElement, text: str) -> None:
        """Type text with human-like patterns
        
        Args:
            element: Web element to type into
            text: Text to type
            
        Raises:
            Exception: If typing fails through both normal and JavaScript methods
        """
        try:
            # Try normal typing first
            element.clear()
            element.send_keys(text)
        except Exception as e:
            logger.error(f"Failed to type text: {str(e)}")
            # Fall back to JavaScript if normal typing fails
            try:
                driver = element.parent
                driver.execute_script("arguments[0].value = arguments[1];", element, text)
            except Exception as e2:
                logger.error(f"Failed to set value via JavaScript: {str(e2)}")
                raise


class WebAuthManager:
    """Web authentication management system"""
    
    def __init__(self, driver: webdriver.Chrome):
        """Initialize WebAuthManager
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    def login(self, 
             url: str,
             credentials: Dict[str, str],
             selectors: Dict[str, str],
             auth_type: str = "form",
             wait_for: Optional[str] = None) -> Dict[str, Any]:
        """Handle website login process
        
        Args:
            url: Login page URL
            credentials: Login credentials (username, password)
            selectors: CSS selectors for login form elements
            auth_type: Authentication type (form, oauth, api)
            wait_for: Optional selector to wait for after login
            
        Returns:
            Dict[str, Any]: Login result with success status and message
        """
        try:
            if auth_type == "form":
                return self._handle_form_login(url, credentials, selectors, wait_for)
            elif auth_type == "oauth":
                return self._handle_oauth_login(url, credentials, selectors, wait_for)
            elif auth_type == "api":
                return self._handle_api_login(url, credentials)
            else:
                return {"success": False, "message": f"Unsupported auth type: {auth_type}"}
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return {"success": False, "message": str(e)}

    def _handle_form_login(self, url: str, credentials: Dict[str, str], 
                         selectors: Dict[str, str], wait_for: Optional[str]) -> Dict[str, Any]:
        """Handle form-based login process
        
        Implements a human-like login process with appropriate delays and checks
        for various security measures like CAPTCHA.
        
        Args:
            url: Login page URL
            credentials: Login credentials
            selectors: Form element selectors
            wait_for: Optional element to wait for after login
            
        Returns:
            Dict[str, Any]: Login result with success status and message
        """
        try:
            # Load page
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            
            # Find username field
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors["username"]))
            )
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", username_field)
            time.sleep(0.5)  # Wait for scroll
            
            # Type like a human
            username_field.clear()
            HumanEmulator.simulate_typing(username_field, credentials["username"])
            
            # Natural delay
            time.sleep(random.uniform(0.5, 1.0))
            
            # Handle password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, selectors["password"])
            self.driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
            time.sleep(0.5)
            
            password_field.clear()
            HumanEmulator.simulate_typing(password_field, credentials["password"])
            
            # Natural delay
            time.sleep(random.uniform(0.8, 1.2))
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, selectors["submit"])
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(0.5)
            
            # Use JavaScript click for reliability
            self.driver.execute_script("arguments[0].click();", login_button)
            
            # Wait for response
            time.sleep(2)
            
            # Special handling for specific sites
            if "naver.com" in url:
                # Check for reCAPTCHA
                recaptcha_frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe[title*='recaptcha']")
                if recaptcha_frames:
                    return {"success": False, "message": "Login requires reCAPTCHA verification"}
                
                # Check for standard CAPTCHA
                if self.driver.find_elements(By.CSS_SELECTOR, "#captcha"):
                    return {"success": False, "message": "Login requires CAPTCHA verification"}
                
                # Check for various error conditions
                error_selectors = [
                    "#err_common",      # General error
                    ".login_error",     # Login error
                    "#err_capslock",    # Caps Lock error
                    "#err_empty_id",    # Empty ID error
                    "#err_empty_pw",    # Empty password error
                    ".error_message",   # Other error messages
                    ".error"           # Additional error class
                ]
                for selector in error_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            try:
                                if element.is_displayed():
                                    error_text = element.text.strip()
                                    if error_text:
                                        return {"success": False, "message": f"Login failed - {error_text}"}
                            except:
                                continue
                
                # Check for 2-step authentication
                if self.driver.find_elements(By.CSS_SELECTOR, ".2step_auth"):
                    return {"success": False, "message": "2-step verification required"}
            
            # Check for general login failure
            # 1. Check if login form still exists and is visible
            if self.driver.find_elements(By.CSS_SELECTOR, selectors["username"]) and \
               self.driver.find_elements(By.CSS_SELECTOR, selectors["password"]):
                try:
                    username_visible = self.driver.find_element(By.CSS_SELECTOR, selectors["username"]).is_displayed()
                    password_visible = self.driver.find_element(By.CSS_SELECTOR, selectors["password"]).is_displayed()
                    if username_visible and password_visible:
                        return {"success": False, "message": "Login failed - form still visible"}
                except:
                    pass
            
            # Check for URL change (to ensure not logged in)
            current_url = self.driver.current_url
            if url == current_url:
                return {"success": False, "message": "Login failed - URL did not change"}
            
            # Save session information
            cookies = self.driver.get_cookies()
            local_storage = self.driver.execute_script("return window.localStorage;")
            session_storage = self.driver.execute_script("return window.sessionStorage;")
            
            return {
                "success": True,
                "message": "Login successful",
                "session_data": {
                    "cookies": cookies,
                    "localStorage": local_storage,
                    "sessionStorage": session_storage
                }
            }
            
        except TimeoutException:
            return {"success": False, "message": "Login timeout - element not found"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _handle_oauth_login(self, url: str, credentials: Dict[str, str],
                         selectors: Dict[str, str], wait_for: Optional[str]) -> Dict[str, Any]:
        """OAuth login process
        
        OAuth implementation will be added later
        """
        return {"success": False, "message": "OAuth login not implemented yet"}

    def _handle_api_login(self, url: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """API login process
        
        API login implementation will be added later
        """
        return {"success": False, "message": "API login not implemented yet"}

class SeleniumService:
    def __init__(self):
        self.driver = None
        
    def setup_browser(self) -> None:
        """Initialize Chrome browser"""
        if self.driver is not None:
            return
            
        options = webdriver.ChromeOptions()
        
        try:
            # Get user's Chrome profile path
            chrome_profile = get_chrome_profile_path()
            logger.info(f"Using Chrome profile path: {chrome_profile}")
            options.add_argument(f'--user-data-dir={chrome_profile}')
        except Exception as e:
            logger.error(f"Failed to set Chrome profile path: {str(e)}")
            logger.warning("Continuing without user profile...")
        
        # Additional settings for automation detection bypass
        options.add_argument('--headless=new')  # Enable headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-notifications')
        
        # Set binary location from environment variable
        binary_location = os.getenv('CHROME_BINARY_LOCATION')
        if binary_location:
            options.binary_location = binary_location
            
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def _ensure_driver(self) -> None:
        """Ensure driver is initialized"""
        if self.driver is None:
            self.setup_browser()

    def tool_open_browser(self) -> Dict[str, Any]:
        """Open a new Chrome browser instance.
        
        This tool initializes a new Chrome browser window. If a browser instance
        already exists, it will reuse that instance.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - message (str): Status message
        
        Example:
            {"tool": "open_browser"}
        """
        try:
            self._ensure_driver()
            return {"success": True, "message": "Browser opened successfully"}
        except WebDriverException as e:
            return {"success": False, "message": str(e)}

    def tool_close_browser(self) -> Dict[str, Any]:
        """Close the browser instance.
        
        This tool closes the current Chrome browser window and cleans up resources.
        It's safe to call this even if no browser is open.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - message (str): Status message
        
        Example:
            {"tool": "close_browser"}
        """
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                return {"success": True, "message": "Browser closed successfully"}
            except WebDriverException as e:
                return {"success": False, "message": str(e)}
        return {"success": True, "message": "No browser instance to close"}

    def tool_navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL.
        
        This tool navigates the browser to the specified URL. If no browser
        is open, it will automatically open one.
        
        Args:
            url (str): The URL to navigate to (must include protocol, e.g., 'https://')
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - message (str): Status message
        
        Example:
            {"tool": "navigate", "args": {"url": "https://www.example.com"}}
        """
        try:
            self._ensure_driver()
            self.driver.get(url)
            return {"success": True, "message": f"Navigated to {url}"}
        except WebDriverException as e:
            return {"success": False, "message": str(e)}

    def tool_click(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Click an element on the page.
        
        This tool finds and clicks an element on the page using either CSS selector
        or XPath. It will wait for the element to be clickable before attempting
        to click it.
        
        Args:
            selector (str): The selector to find the element
            by (str, optional): The selector type. Either "css" or "xpath". Defaults to "css"
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - message (str): Status message
        
        Example:
            {"tool": "click", "args": {"selector": "#submit-button"}}
            {"tool": "click", "args": {"selector": "//button[@type='submit']", "by": "xpath"}}
        """
        try:
            self._ensure_driver()
            by_method = By.CSS_SELECTOR if by == "css" else By.XPATH
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_method, selector))
            )
            element.click()
            return {"success": True, "message": f"Clicked element: {selector}"}
        except (TimeoutException, WebDriverException) as e:
            return {"success": False, "message": str(e)}

    def tool_type(self, selector: str, text: str, by: str = "css") -> Dict[str, Any]:
        """Type text into an element.
        
        This tool finds an input element and types the specified text into it.
        It will clear any existing text in the element before typing.
        
        Args:
            selector (str): The selector to find the element
            text (str): The text to type into the element
            by (str, optional): The selector type. Either "css" or "xpath". Defaults to "css"
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - message (str): Status message
        
        Example:
            {"tool": "type", "args": {"selector": "#search-input", "text": "search query"}}
            {"tool": "type", "args": {"selector": "//input[@name='q']", "text": "search", "by": "xpath"}}
        """
        try:
            self._ensure_driver()
            by_method = By.CSS_SELECTOR if by == "css" else By.XPATH
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_method, selector))
            )
            element.clear()
            element.send_keys(text)
            return {"success": True, "message": f"Typed text into element: {selector}"}
        except (TimeoutException, WebDriverException) as e:
            return {"success": False, "message": str(e)}

    def tool_get_text(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Get text from an element.
        
        This tool finds an element and returns its text content.
        
        Args:
            selector (str): The selector to find the element
            by (str, optional): The selector type. Either "css" or "xpath". Defaults to "css"
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - message (str): Status message
                - data (str): The text content of the element
        
        Example:
            {"tool": "get_text", "args": {"selector": "h1"}}
            {"tool": "get_text", "args": {"selector": "//div[@class='content']", "by": "xpath"}}
        """
        try:
            self._ensure_driver()
            by_method = By.CSS_SELECTOR if by == "css" else By.XPATH
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_method, selector))
            )
            text = element.text
            return {"success": True, "message": "Text retrieved successfully", "data": text}
        except (TimeoutException, WebDriverException) as e:
            return {"success": False, "message": str(e)}

    def tool_get_elements(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Get multiple elements matching a selector.
        
        This tool finds all elements matching the selector and returns their text
        content and HTML.
        
        Args:
            selector (str): The selector to find the elements
            by (str, optional): The selector type. Either "css" or "xpath". Defaults to "css"
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - message (str): Status message
                - data (List[Dict]): List of elements, each containing:
                    - text (str): The text content of the element
                    - html (str): The outer HTML of the element
        
        Example:
            {"tool": "get_elements", "args": {"selector": ".item"}}
            {"tool": "get_elements", "args": {"selector": "//li[@class='item']", "by": "xpath"}}
        """
        try:
            self._ensure_driver()
            by_method = By.CSS_SELECTOR if by == "css" else By.XPATH
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((by_method, selector))
            )
            result = [{"text": el.text, "html": el.get_attribute("outerHTML")} for el in elements]
            return {"success": True, "message": f"Found {len(result)} elements", "data": result}
        except (TimeoutException, WebDriverException) as e:
            return {"success": False, "message": str(e)}

    def tool_save_credentials(self, site: str, username: str, password: str) -> Dict[str, Any]:
        """
        Securely save credentials
        
        Args:
            site: Website domain
            username: User's username
            password: Password
        """
        success = CredentialManager.save_credentials(site, username, password)
        return {
            "success": success,
            "message": "Credentials saved successfully" if success else "Failed to save credentials"
        }

    def tool_get_credentials(self, site: str, username: str) -> Dict[str, Any]:
        """
        Retrieve stored credentials from system keychain
        
        Args:
            site: Website domain
            username: User's username
        """
        password = CredentialManager.get_credentials(site, username)
        return {
            "success": bool(password),
            "credentials": {"username": username, "password": password} if password else None,
            "message": "Credentials retrieved successfully" if password else "Credentials not found"
        }

    def tool_web_login(self, url: str, credentials: Dict[str, str],
                     selectors: Dict[str, str], auth_type: str = "form",
                     wait_for: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform website login

        This tool attempts to log in to the provided URL. It waits for automatic
        input prevention (CAPTCHA) to be detected before allowing the user to manually resolve it.

        Args:
            url (str): Login page URL
            credentials (Dict[str, str]): Login credentials
                - username: User ID
                - password: Password
            selectors (Dict[str, str]): CSS selectors for login form elements
                - username: ID input field selector
                - password: Password input field selector
                - submit: Login button selector
            auth_type (str, optional): Authentication type. Defaults to "form"
                - form: Regular form-based login
                - oauth: OAuth authentication
                - api: API-based authentication
            wait_for (Optional[str], optional): CSS selector for element to wait for after login

        Returns:
            Dict[str, Any]: Login result
                - success (bool): Login success status
                - message (str): Status message
                - session_data (Dict): Login success session information
                    - cookies: Cookie information
                    - localStorage: Local storage data
                    - sessionStorage: Session storage data

        Special handling:
            1. CAPTCHA detection
                - If reCAPTCHA or standard CAPTCHA is detected, wait for user to manually resolve
                - Automatically continue login process after resolution
            2. Naver login
                - Automatic detection of various special situations like automatic input prevention, 2-step authentication
                - Detailed error message analysis and return

        Example:
            >>> result = tool_web_login(
            ...     url="https://nid.naver.com/nidlogin.login",
            ...     credentials={
            ...         "username": "your_username",
            ...         "password": "your_password"
            ...     },
            ...     selectors={
            ...         "username": "#id",
            ...         "password": "#pw",
            ...         "submit": ".btn_login"
            ...     }
            ... )
            >>> if not result["success"] and "CAPTCHA" in result["message"]:
            ...     # Wait for user input for CAPTCHA resolution
            ...     print("Please solve the CAPTCHA in the browser")
        """
        try:
            # Set default selectors for Naver login page
            if "naver.com" in url:
                selectors = {
                    "username": "#id",
                    "password": "#pw",
                    "submit": ".btn_login"
                }
            
            auth = WebAuthManager(self.driver)
            result = auth.login(url, credentials, selectors, auth_type, wait_for)
            return result
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_current_url(self) -> Dict[str, Any]:
        """Return the current page's URL."""
        try:
            url = self.driver.current_url
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_title(self) -> Dict[str, Any]:
        """Return the current page's title."""
        try:
            title = self.driver.title
            return {"success": True, "title": title}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_page_source(self) -> Dict[str, Any]:
        """Return the current page's HTML source."""
        try:
            source = self.driver.page_source
            return {"success": True, "source": source}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_refresh(self) -> Dict[str, Any]:
        """Refresh the current page."""
        try:
            self.driver.refresh()
            return {"success": True, "message": "Page refreshed successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_back(self) -> Dict[str, Any]:
        """Navigate back in the browser history."""
        try:
            self.driver.back()
            return {"success": True, "message": "Navigated back successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_forward(self) -> Dict[str, Any]:
        """Navigate forward in the browser history."""
        try:
            self.driver.forward()
            return {"success": True, "message": "Navigated forward successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_execute_script(self, script: str, *args) -> Dict[str, Any]:
        """Execute JavaScript code."""
        try:
            result = self.driver.execute_script(script, *args)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_cookies(self) -> Dict[str, Any]:
        """Return all cookies from the current page."""
        try:
            cookies = self.driver.get_cookies()
            return {"success": True, "cookies": cookies}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_add_cookie(self, cookie: Dict[str, Any]) -> Dict[str, Any]:
        """Add a cookie."""
        try:
            self.driver.add_cookie(cookie)
            return {"success": True, "message": "Cookie added successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_delete_cookie(self, name: str) -> Dict[str, Any]:
        """Delete a specific cookie."""
        try:
            self.driver.delete_cookie(name)
            return {"success": True, "message": f"Cookie '{name}' deleted successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_delete_all_cookies(self) -> Dict[str, Any]:
        """Delete all cookies."""
        try:
            self.driver.delete_all_cookies()
            return {"success": True, "message": "All cookies deleted successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_set_window_size(self, width: int, height: int) -> Dict[str, Any]:
        """Set the browser window size."""
        try:
            self.driver.set_window_size(width, height)
            return {"success": True, "message": f"Window size set to {width}x{height}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_window_size(self) -> Dict[str, Any]:
        """Return the current browser window size."""
        try:
            size = self.driver.get_window_size()
            return {"success": True, "size": size}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_maximize_window(self) -> Dict[str, Any]:
        """Maximize the browser window."""
        try:
            self.driver.maximize_window()
            return {"success": True, "message": "Window maximized successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_minimize_window(self) -> Dict[str, Any]:
        """Minimize the browser window."""
        try:
            self.driver.minimize_window()
            return {"success": True, "message": "Window minimized successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_fullscreen_window(self) -> Dict[str, Any]:
        """Switch the browser window to full screen."""
        try:
            self.driver.fullscreen_window()
            return {"success": True, "message": "Window set to fullscreen successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Save a screenshot of the current page."""
        try:
            if filename:
                self.driver.save_screenshot(filename)
                return {"success": True, "message": f"Screenshot saved as {filename}"}
            else:
                screenshot = self.driver.get_screenshot_as_base64()
                return {"success": True, "screenshot": screenshot}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_switch_to_frame(self, frame_reference: Union[str, int, WebElement]) -> Dict[str, Any]:
        """Switch to a specific frame."""
        try:
            self.driver.switch_to.frame(frame_reference)
            return {"success": True, "message": "Switched to frame successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_switch_to_default_content(self) -> Dict[str, Any]:
        """Switch back to default content."""
        try:
            self.driver.switch_to.default_content()
            return {"success": True, "message": "Switched to default content successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_switch_to_window(self, window_handle: str) -> Dict[str, Any]:
        """Switch to a specific window."""
        try:
            self.driver.switch_to.window(window_handle)
            return {"success": True, "message": "Switched to window successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_window_handles(self) -> Dict[str, Any]:
        """Return all window handles."""
        try:
            self._ensure_driver()
            handles = self.driver.window_handles
            return {"success": True, "handles": handles}
        except WebDriverException as e:
            return {"success": False, "message": str(e)}


    def tool_get_log(self, log_type: str) -> Dict[str, Any]:
        """Retrieve browser logs."""
        try:
            logs = self.driver.get_log(log_type)
            return {"success": True, "logs": logs}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_implicitly_wait(self, seconds: int) -> Dict[str, Any]:
        """Set implicitly wait time."""
        try:
            self.driver.implicitly_wait(seconds)
            return {"success": True, "message": f"Implicit wait set to {seconds} seconds"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_set_page_load_timeout(self, seconds: int) -> Dict[str, Any]:
        """Set page load timeout."""
        try:
            self.driver.set_page_load_timeout(seconds)
            return {"success": True, "message": f"Page load timeout set to {seconds} seconds"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_set_script_timeout(self, seconds: int) -> Dict[str, Any]:
        """Set script execution timeout."""
        try:
            self.driver.set_script_timeout(seconds)
            return {"success": True, "message": f"Script timeout set to {seconds} seconds"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_sample(self, seconds: int) -> Dict[str, Any]:
        """Set Sample execution timeout."""
        try:
            self.driver.set_script_timeout(seconds)
            return {"success": True, "message": f"Script timeout set to {seconds} seconds"}
        except Exception as e:
            return {"success": False, "message": str(e)}
