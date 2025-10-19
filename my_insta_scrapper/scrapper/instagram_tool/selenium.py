from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import os
import time

class InstagramSession:
    def __init__(self):
         
        """Initialize variables and paths."""
        # Define the base directory where everything will be stored
        self.base_path = r"scrapper\instagram_tool"
        # os.makedirs(self.base_path, exist_ok=True)

        # Define file paths
        self.session_file = os.path.join(self.base_path, "instagram_session.pkl")
        self.cookies_file = os.path.join(self.base_path, "instagram_cookies.pkl")
        # self.proxies = proxies  # Store proxy configuration as dictionary
        self.driver = None

        # self.driver = None
        # self.session_file = "instagram_session.pkl"
        # self.cookies_file = "instagram_cookies.pkl"
        # # self.proxies = proxies  # Store proxy configuration as dictionary

    def setup_driver(self):
        """Initialize Chrome driver with options"""
        options = webdriver.ChromeOptions()

 # Add proxy if provided
        # if self.proxies:
        # # Extract proxy from the dictionary (use http proxy by default)
        #      proxy_url = self.proxies.get('http') or self.proxies.get('https')
        #      if proxy_url:
        #     # Remove the protocol prefix if present
        #         proxy_string = proxy_url.replace('http://', '').replace('https://', '')
        #         options.add_argument(f'--proxy-server={proxy_string}')
        #         print(f"Using proxy: {proxy_string}")

        # options.add_argument("--headless")  # Uncomment for headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
        
    def save_session(self):
        """Save cookies to file for session persistence"""
        try:
            # Navigate to Instagram main page first to get proper cookies
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            

            # Define the save directory
            cookies = self.driver.get_cookies()

            with open(self.cookies_file, 'wb') as file:
                pickle.dump(cookies, file)

            print(f"Session saved successfully at: {self.cookies_file}")

        except Exception as e:
            print(f"Error saving session: {e}")
            
    def load_session(self):
        """Load cookies from file and add to driver"""
        try:
            if os.path.exists(self.cookies_file):
                # First go to the domain to set cookies properly
                self.driver.get("https://www.instagram.com/")
                time.sleep(2)
                
                with open(self.cookies_file, 'rb') as file:
                    cookies = pickle.load(file)
                
                # Clear existing cookies and add saved ones
                self.driver.delete_all_cookies()
                
                for cookie in cookies:
                    # Fix domain for cookies if needed
                    if 'instagram.com' not in cookie.get('domain', ''):
                        cookie['domain'] = '.instagram.com'
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Could not add cookie: {e}")
                        continue
                
                print("Session loaded successfully!")
                return True
            return False
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
            
    def is_logged_in(self):
        """Check if user is logged in using more reliable methods"""
        try:
            # Go to main page
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            # Method 1: Check for presence of navigation bar that only appears when logged in
            logged_in_indicators = [
                "//a[contains(@href, '/direct/inbox/')]",  # DM icon
                "//a[contains(@href, '/accounts/activity/')]",  # Activity icon
                "//a[contains(@href, '/create/')]"  # Create post icon
            ]
            
            for indicator in logged_in_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements:
                        print("Logged in detected via navigation elements")
                        return True
                except:
                    continue
            
            # Method 2: Check for login page elements (negative test)
            login_indicators = [
                "//button[contains(text(), 'Log in')]",
                "//input[@name='username']",
                "//input[@name='password']"
            ]
            
            for indicator in login_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements:
                        print("Not logged in - login form detected")
                        return False
                except:
                    continue
            
            # Method 3: Try to access profile
            try:
                self.driver.get("https://www.instagram.com/accounts/edit/")
                time.sleep(2)
                
                if "accounts/login" in self.driver.current_url:
                    return False
                
                # Check for profile edit elements
                profile_elements = self.driver.find_elements(By.XPATH, "//input[@name='firstName']")
                if profile_elements:
                    print("Logged in detected via profile edit page")
                    return True
            except:
                pass
            
            print("Login status uncertain")
            return False
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
            
    def login(self, username, password):
        """Perform login with credentials"""
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            wait = WebDriverWait(self.driver, 15)
            
            # Wait for and fill username
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.clear()
            username_field.send_keys(username)
            
            # Fill password
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete - handle possible "Save Info" dialog
            try:
                wait.until(EC.url_contains("instagram.com"))
                time.sleep(5)
                
                # Handle "Save Login Info" prompt if it appears
                try:
                    not_now_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
                    not_now_btn.click()
                    time.sleep(2)
                except:
                    pass
                
                # Handle "Turn on Notifications" prompt if it appears
                try:
                    not_now_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
                    not_now_btn.click()
                    time.sleep(2)
                except:
                    pass
                
            except Exception as e:
                print(f"Wait for login completion failed: {e}")
            
            # Check if login was successful
            if "accounts/login" in self.driver.current_url:
                print("Login failed! Please check credentials.")
                return False
                
            print("Login successful!")
            self.save_session()
            return True
            
        except Exception as e:
            print(f"Login error: {e}")
            return False
            
    def initialize_session(self, username=None, password=None):
        """Main method to initialize session - tries to use saved session first"""
        self.setup_driver()
        
        # First, try to load existing session
        if self.load_session():
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(5)
            
            # Check if we're actually logged in
            if self.is_logged_in():
                print("Successfully logged in using saved session!")
                return True
            else:
                print("Saved session expired or invalid.")
                # Remove invalid session file
                if os.path.exists(self.cookies_file):
                    os.remove(self.cookies_file)
        
        # If no valid session, perform fresh login
        if username and password:
            print("Performing fresh login...")
            success = self.login(username, password)
            if success:
                # Verify login worked
                time.sleep(3)
                return self.is_logged_in()
            return False
        else:
            print("No credentials provided for fresh login.")
            return False
            
    def perform_action(self, url):
        """Example action after login"""
        try:
            self.driver.get(url)
            time.sleep(30)

            # Get the complete page HTML
            page_html = self.driver.page_source

            # Define the target directory
            save_path = r"scrapper\instagram_tool"

            # # Make sure the directory exists
            # os.makedirs(save_path, exist_ok=True)

            # Create the full file path
            file_path = os.path.join(save_path, "full_page.html")

            # Save the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_html)
            
            print(f"Page HTML saved to {file_path}")
            
        except Exception as e:
            print(f"Error performing action: {e}")

        finally:
        # Close the browser at the very end
           if self.driver:
               self.driver.quit()    
