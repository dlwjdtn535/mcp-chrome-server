import logging
import random
import time
import os
from typing import Optional, Dict, Any, Union

import keyring
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

def get_chrome_profile_path() -> str:
    """사용자의 Chrome 프로필 경로를 가져옵니다.
    
    환경 변수에서 CHROME_PROFILE_PATH를 찾아 반환합니다.
    환경 변수가 설정되어 있지 않으면 기본 경로를 반환합니다.
    
    Returns:
        str: Chrome 프로필 경로
        
    Raises:
        Exception: 프로필 경로를 찾을 수 없는 경우
    """
    # 환경 변수에서 프로필 경로 확인
    profile_path = os.getenv('CHROME_PROFILE_PATH')
    if profile_path:
        return profile_path
        
    # 기본 프로필 경로 (OS별)
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
    """보안 자격 증명 관리"""
    
    @staticmethod
    def save_credentials(site: str, username: str, password: str) -> bool:
        """자격 증명을 시스템 키체인에 안전하게 저장"""
        try:
            keyring.set_password(site, username, password)
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
            return False
    
    @staticmethod
    def get_credentials(site: str, username: str) -> Optional[str]:
        """저장된 자격 증명 조회"""
        try:
            return keyring.get_password(site, username)
        except Exception as e:
            logger.error(f"Failed to get credentials: {str(e)}")
            return None

class HumanEmulator:
    """사람의 행동을 모방하는 도구"""
    
    @staticmethod
    def get_random_delay():
        """실제 사람의 타이핑 패턴을 모방한 지연 시간"""
        return random.uniform(0.1, 0.3)
    
    @staticmethod
    def simulate_typing(element, text: str):
        """사람과 유사한 타이핑 패턴으로 텍스트 입력"""
        try:
            # JavaScript로 값 설정 (기본)
            element.clear()
            element.send_keys(text)
        except Exception as e:
            logger.error(f"Failed to type text: {str(e)}")
            # 실패 시 JavaScript로 직접 값 설정
            try:
                driver = element.parent
                driver.execute_script("arguments[0].value = arguments[1];", element, text)
            except Exception as e2:
                logger.error(f"Failed to set value via JavaScript: {str(e2)}")
                raise


class WebAuthManager:
    """웹 인증 관리자"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    def login(self, 
             url: str,
             credentials: Dict[str, str],
             selectors: Dict[str, str],
             auth_type: str = "form",
             wait_for: Optional[str] = None) -> Dict[str, Any]:
        """
        웹사이트 로그인 처리
        
        Args:
            url: 로그인 페이지 URL
            credentials: 로그인 정보 (username, password 등)
            selectors: 로그인 폼 요소의 선택자들 (username, password, submit 필수)
            auth_type: 인증 방식 (form, oauth, api 등)
            wait_for: 로그인 성공 후 기다릴 요소
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
        """폼 기반 로그인 처리"""
        try:
            # 페이지 로드
            self.driver.get(url)
            time.sleep(2)  # 페이지 로드 대기
            
            # 사용자명 입력 필드 찾기
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors["username"]))
            )
            
            # 요소가 보이도록 스크롤
            self.driver.execute_script("arguments[0].scrollIntoView(true);", username_field)
            time.sleep(0.5)  # 스크롤 대기
            
            # 사람처럼 타이핑
            username_field.clear()
            HumanEmulator.simulate_typing(username_field, credentials["username"])
            
            # 잠시 대기
            time.sleep(random.uniform(0.5, 1.0))
            
            # 비밀번호 입력
            password_field = self.driver.find_element(By.CSS_SELECTOR, selectors["password"])
            self.driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
            time.sleep(0.5)
            
            password_field.clear()
            HumanEmulator.simulate_typing(password_field, credentials["password"])
            
            # 잠시 대기
            time.sleep(random.uniform(0.8, 1.2))
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.CSS_SELECTOR, selectors["submit"])
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(0.5)
            
            # JavaScript로 클릭 (더 안정적)
            self.driver.execute_script("arguments[0].click();", login_button)
            
            # 로그인 성공/실패 확인
            time.sleep(2)  # 페이지 반응 대기
            
            # 사이트별 특수 처리
            if "naver.com" in url:
                # reCAPTCHA iframe 확인
                recaptcha_frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe[title*='recaptcha']")
                if recaptcha_frames:
                    return {"success": False, "message": "Login requires reCAPTCHA verification"}
                
                # 일반 CAPTCHA 확인
                if self.driver.find_elements(By.CSS_SELECTOR, "#captcha"):
                    return {"success": False, "message": "Login requires CAPTCHA verification"}
                
                # 네이버 로그인 실패 감지
                error_selectors = [
                    "#err_common",  # 일반적인 에러 메시지
                    ".login_error",  # 로그인 에러
                    "#err_capslock",  # Caps Lock 에러
                    "#err_empty_id",  # 빈 아이디 에러
                    "#err_empty_pw",  # 빈 비밀번호 에러
                    ".error_message",  # 기타 에러 메시지
                    ".error"  # 추가 에러 클래스
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
                
                # 2단계 인증 페이지 감지
                if self.driver.find_elements(By.CSS_SELECTOR, ".2step_auth"):
                    return {"success": False, "message": "2-step verification required"}
            
            # 일반적인 로그인 실패 감지
            # 1. 로그인 폼이 여전히 존재하고 표시되는지 확인
            if self.driver.find_elements(By.CSS_SELECTOR, selectors["username"]) and \
               self.driver.find_elements(By.CSS_SELECTOR, selectors["password"]):
                try:
                    username_visible = self.driver.find_element(By.CSS_SELECTOR, selectors["username"]).is_displayed()
                    password_visible = self.driver.find_element(By.CSS_SELECTOR, selectors["password"]).is_displayed()
                    if username_visible and password_visible:
                        return {"success": False, "message": "Login failed - form still visible"}
                except:
                    pass
            
            # URL 변경 확인 (로그인 페이지를 벗어났는지)
            current_url = self.driver.current_url
            if url == current_url:
                return {"success": False, "message": "Login failed - URL did not change"}
            
            # 세션 정보 저장
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
        """OAuth 로그인 처리"""
        # OAuth 구현은 추후 추가
        return {"success": False, "message": "OAuth login not implemented yet"}

    def _handle_api_login(self, url: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """API 로그인 처리"""
        # API 로그인 구현은 추후 추가
        return {"success": False, "message": "API login not implemented yet"}

class SeleniumService:
    def __init__(self):
        self.driver = None
        
    def setup_browser(self) -> None:
        """Chrome 브라우저 초기화 with undetected-chromedriver"""
        if self.driver is not None:
            return
            
        options = uc.ChromeOptions()
        
        try:
            # 사용자의 크롬 프로필 경로를 가져옴
            chrome_profile = get_chrome_profile_path()
            logger.info(f"Using Chrome profile path: {chrome_profile}")
            options.add_argument(f'--user-data-dir={chrome_profile}')
            options.add_argument('--profile-directory=Default')  # 기본 프로필 사용
        except Exception as e:
            logger.error(f"Failed to set Chrome profile path: {str(e)}")
            logger.warning("Continuing without user profile...")
        
        # 자동화 감지 우회를 위한 추가 설정
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-notifications')
        
        self.driver = uc.Chrome(options=options)
        
        # 자동화 감지 플래그 제거
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.implicitly_wait(10)

    def _ensure_driver(self) -> None:
        """드라이버가 초기화되어 있는지 확인"""
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
        자격 증명을 안전하게 저장
        
        Args:
            site: 웹사이트 도메인
            username: 사용자 이름
            password: 비밀번호
        """
        success = CredentialManager.save_credentials(site, username, password)
        return {
            "success": success,
            "message": "Credentials saved successfully" if success else "Failed to save credentials"
        }

    def tool_get_credentials(self, site: str, username: str) -> Dict[str, Any]:
        """
        저장된 자격 증명 조회
        
        Args:
            site: 웹사이트 도메인
            username: 사용자 이름
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
        웹사이트 로그인 수행

        이 도구는 제공된 URL로 이동하여 로그인을 시도합니다. 자동입력방지(CAPTCHA)가 
        감지되면 사용자가 직접 해결할 때까지 대기합니다.

        Args:
            url (str): 로그인 페이지 URL
            credentials (Dict[str, str]): 로그인 정보
                - username: 사용자 아이디
                - password: 비밀번호
            selectors (Dict[str, str]): 로그인 폼 요소의 선택자들
                - username: 아이디 입력 필드 선택자
                - password: 비밀번호 입력 필드 선택자
                - submit: 로그인 버튼 선택자
            auth_type (str, optional): 인증 방식. Defaults to "form"
                - form: 일반적인 폼 기반 로그인
                - oauth: OAuth 인증
                - api: API 기반 인증
            wait_for (Optional[str], optional): 로그인 성공 후 기다릴 요소의 선택자

        Returns:
            Dict[str, Any]: 로그인 결과
                - success (bool): 로그인 성공 여부
                - message (str): 상태 메시지
                - session_data (Dict): 로그인 성공시 세션 정보
                    - cookies: 쿠키 정보
                    - localStorage: 로컬 스토리지 데이터
                    - sessionStorage: 세션 스토리지 데이터

        특별한 처리:
            1. CAPTCHA 감지
                - reCAPTCHA나 일반 CAPTCHA가 감지되면 사용자가 직접 해결할 때까지 대기
                - 해결 후 자동으로 로그인 프로세스 계속 진행
            2. 네이버 로그인
                - 자동입력방지, 2단계 인증 등 특수한 상황 자동 감지
                - 에러 메시지 상세 분석 및 반환

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
            ...     # CAPTCHA 해결을 위해 사용자 입력 대기
            ...     print("Please solve the CAPTCHA in the browser")
        """
        try:
            # 네이버 로그인 페이지인 경우 기본 선택자 설정
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
        """현재 페이지의 URL을 반환합니다."""
        try:
            url = self.driver.current_url
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_title(self) -> Dict[str, Any]:
        """현재 페이지의 제목을 반환합니다."""
        try:
            title = self.driver.title
            return {"success": True, "title": title}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_page_source(self) -> Dict[str, Any]:
        """현재 페이지의 HTML 소스를 반환합니다."""
        try:
            source = self.driver.page_source
            return {"success": True, "source": source}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_refresh(self) -> Dict[str, Any]:
        """현재 페이지를 새로고침합니다."""
        try:
            self.driver.refresh()
            return {"success": True, "message": "Page refreshed successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_back(self) -> Dict[str, Any]:
        """브라우저 히스토리에서 뒤로 이동합니다."""
        try:
            self.driver.back()
            return {"success": True, "message": "Navigated back successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_forward(self) -> Dict[str, Any]:
        """브라우저 히스토리에서 앞으로 이동합니다."""
        try:
            self.driver.forward()
            return {"success": True, "message": "Navigated forward successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_execute_script(self, script: str, *args) -> Dict[str, Any]:
        """JavaScript 코드를 실행합니다."""
        try:
            result = self.driver.execute_script(script, *args)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_cookies(self) -> Dict[str, Any]:
        """현재 페이지의 모든 쿠키를 반환합니다."""
        try:
            cookies = self.driver.get_cookies()
            return {"success": True, "cookies": cookies}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_add_cookie(self, cookie: Dict[str, Any]) -> Dict[str, Any]:
        """쿠키를 추가합니다."""
        try:
            self.driver.add_cookie(cookie)
            return {"success": True, "message": "Cookie added successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_delete_cookie(self, name: str) -> Dict[str, Any]:
        """특정 이름의 쿠키를 삭제합니다."""
        try:
            self.driver.delete_cookie(name)
            return {"success": True, "message": f"Cookie '{name}' deleted successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_delete_all_cookies(self) -> Dict[str, Any]:
        """모든 쿠키를 삭제합니다."""
        try:
            self.driver.delete_all_cookies()
            return {"success": True, "message": "All cookies deleted successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_set_window_size(self, width: int, height: int) -> Dict[str, Any]:
        """브라우저 창 크기를 설정합니다."""
        try:
            self.driver.set_window_size(width, height)
            return {"success": True, "message": f"Window size set to {width}x{height}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_window_size(self) -> Dict[str, Any]:
        """현재 브라우저 창 크기를 반환합니다."""
        try:
            size = self.driver.get_window_size()
            return {"success": True, "size": size}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_maximize_window(self) -> Dict[str, Any]:
        """브라우저 창을 최대화합니다."""
        try:
            self.driver.maximize_window()
            return {"success": True, "message": "Window maximized successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_minimize_window(self) -> Dict[str, Any]:
        """브라우저 창을 최소화합니다."""
        try:
            self.driver.minimize_window()
            return {"success": True, "message": "Window minimized successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_fullscreen_window(self) -> Dict[str, Any]:
        """브라우저 창을 전체 화면으로 전환합니다."""
        try:
            self.driver.fullscreen_window()
            return {"success": True, "message": "Window set to fullscreen successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """현재 페이지의 스크린샷을 저장합니다."""
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
        """특정 프레임으로 전환합니다."""
        try:
            self.driver.switch_to.frame(frame_reference)
            return {"success": True, "message": "Switched to frame successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_switch_to_default_content(self) -> Dict[str, Any]:
        """기본 컨텐츠로 돌아갑니다."""
        try:
            self.driver.switch_to.default_content()
            return {"success": True, "message": "Switched to default content successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_switch_to_window(self, window_handle: str) -> Dict[str, Any]:
        """특정 윈도우로 전환합니다."""
        try:
            self.driver.switch_to.window(window_handle)
            return {"success": True, "message": "Switched to window successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_get_window_handles(self) -> Dict[str, Any]:
        """모든 윈도우 핸들을 반환합니다."""
        try:
            self._ensure_driver()
            handles = self.driver.window_handles
            return {"success": True, "handles": handles}
        except WebDriverException as e:
            return {"success": False, "message": str(e)}


    def tool_get_log(self, log_type: str) -> Dict[str, Any]:
        """브라우저 로그를 가져옵니다."""
        try:
            logs = self.driver.get_log(log_type)
            return {"success": True, "logs": logs}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_implicitly_wait(self, seconds: int) -> Dict[str, Any]:
        """암시적 대기 시간을 설정합니다."""
        try:
            self.driver.implicitly_wait(seconds)
            return {"success": True, "message": f"Implicit wait set to {seconds} seconds"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_set_page_load_timeout(self, seconds: int) -> Dict[str, Any]:
        """페이지 로드 타임아웃을 설정합니다."""
        try:
            self.driver.set_page_load_timeout(seconds)
            return {"success": True, "message": f"Page load timeout set to {seconds} seconds"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def tool_set_script_timeout(self, seconds: int) -> Dict[str, Any]:
        """스크립트 실행 타임아웃을 설정합니다."""
        try:
            self.driver.set_script_timeout(seconds)
            return {"success": True, "message": f"Script timeout set to {seconds} seconds"}
        except Exception as e:
            return {"success": False, "message": str(e)}
