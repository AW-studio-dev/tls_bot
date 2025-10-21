from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import cv2
import pytesseract
import numpy as np
import time
import random
import logging
from proxy_manager import ProxyManager
from captcha_solver import CaptchaSolver

logging.basicConfig(level=logging.INFO)

class AIAutomation:
    def __init__(self, headless=True):
        self.proxy_manager = ProxyManager()
        self.captcha_solver = CaptchaSolver()
        self.driver = self._create_undetected_driver(headless)
        self.wait = WebDriverWait(self.driver, 20)
        
    def _create_undetected_driver(self, headless):
        proxy = self.proxy_manager.get_proxy()
        proxy_url = proxy['http'] if proxy else None
        
        options = uc.ChromeOptions()
        
        if headless:
            options.add_argument('--headless')
            
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if proxy_url:
            options.add_argument(f'--proxy-server={proxy_url}')
        
        driver = uc.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def human_like_delay(self, min_delay=1, max_delay=3):
        time.sleep(random.uniform(min_delay, max_delay))
    
    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
    
    def take_screenshot(self):
        screenshot = self.driver.get_screenshot_as_png()
        nparr = np.frombuffer(screenshot, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    def extract_text_from_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang='eng+fra')
        return text.lower()
    
    def ai_analyze_page(self):
        screenshot = self.take_screenshot()
        text = self.extract_text_from_image(screenshot)
        
        if 'login' in text or 'connexion' in text or 'connectez-vous' in text:
            return 'login_page'
        elif 'réservez votre rendez-vous' in text or 'prendre rendez-vous' in text:
            return 'booking_page'
        elif 'contactez-nous' in text and 'rendez-vous' in text:
            return 'no_slots_available'
        elif 'calendar' in text or 'date' in text or 'créneaux' in text:
            return 'slots_available'
        elif 'confirmer' in text and 'brouillon' in text:
            return 'application_confirmation'
        elif 'voyagez en groupe' in text or 'liste des demandes' in text:
            return 'travel_groups'
        elif 'france-visas' in text or 'numéro de référence' in text:
            return 'application_form'
        else:
            return 'unknown_page'
    
    def smart_login(self, email, password, country):
        base_url = 'https://visas-fr.tlscontact.com' if country == 'france' else 'https://visas-de.tlscontact.com'
        
        try:
            login_url = f"{base_url}/auth/realms/atlas/protocol/openid-connect/auth"
            self.driver.get(login_url)
            self.human_like_delay()
            
            max_attempts = 3
            for attempt in range(max_attempts):
                page_type = self.ai_analyze_page()
                
                if page_type == 'login_page':
                    try:
                        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
                        password_field = self.driver.find_element(By.NAME, 'password')
                        
                        self.human_type(email_field, email)
                        self.human_like_delay(0.5, 1)
                        self.human_type(password_field, password)
                        self.human_like_delay(0.5, 1)
                        
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
                        submit_btn.click()
                        self.human_like_delay(2, 4)
                        
                        if 'travel-groups' in self.driver.current_url:
                            return True
                    except Exception as e:
                        logging.error(f"Login attempt {attempt + 1} failed: {e}")
                
                self.human_like_delay(2)
            
            return False
            
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False
    
    def navigate_to_booking(self, group_id):
        try:
            self.driver.get(f"https://visas-fr.tlscontact.com/fr-fr/{group_id}/workflow/appointment-booking")
            self.human_like_delay()
            return True
        except:
            return False
    
    def check_availability(self):
        try:
            page_type = self.ai_analyze_page()
            return page_type == 'slots_available'
        except:
            return False
    
    def complete_application_form(self, user_data):
        try:
            if 'application_form' not in self.ai_analyze_page():
                return False
            
            self.human_like_delay()
            
            form_data = {
                'France-Visas Reference': user_data.get('france_visas_ref', ''),
                'First Name': user_data.get('first_name', ''),
                'Last Name': user_data.get('last_name', ''),
                'Passport Number': user_data.get('passport_number', ''),
                'Phone Number': user_data.get('phone_number', '')
            }
            
            for field_name, value in form_data.items():
                if value:
                    try:
                        field = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{field_name}')]/following::input[1]")
                        self.human_type(field, value)
                        self.human_like_delay(0.5, 1)
                    except:
                        continue
            
            submit_btn = self.driver.find_elements(By.XPATH, "//button[contains(., 'Soumettre') or contains(., 'Confirmer')]")
            if submit_btn:
                submit_btn[0].click()
                self.human_like_delay(2, 4)
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Form completion failed: {e}")
            return False
    
    def smart_book_appointment(self):
        try:
            max_attempts = 5
            for attempt in range(max_attempts):
                page_type = self.ai_analyze_page()
                
                if page_type == 'slots_available':
                    book_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Book') or contains(., 'Réserver') or contains(., 'Sélectionner')]")
                    if book_buttons:
                        book_buttons[0].click()
                        self.human_like_delay(2, 4)
                        continue
                
                elif page_type == 'application_confirmation':
                    confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Confirmer')]")
                    if confirm_buttons:
                        confirm_buttons[0].click()
                        self.human_like_delay(2, 4)
                        return True
                
                self.human_like_delay(1)
            
            return False
            
        except Exception as e:
            logging.error(f"Booking failed: {e}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()
