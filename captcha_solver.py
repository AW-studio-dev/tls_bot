import requests
import time
from config import TWOCAPTCHA_API_KEY

class CaptchaSolver:
    def __init__(self):
        self.api_key = TWOCAPTCHA_API_KEY
        self.base_url = "http://2captcha.com"
    
    def solve_recaptcha(self, site_key, page_url):
        if not self.api_key:
            return None
            
        try:
            data = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'page_url': page_url,
                'json': 1
            }
            
            response = requests.post(f"{self.base_url}/in.php", data=data, timeout=30)
            result = response.json()
            
            if result['status'] == 1:
                request_id = result['request']
                
                for _ in range(30):
                    time.sleep(5)
                    result_response = requests.get(
                        f"{self.base_url}/res.php?key={self.api_key}&action=get&id={request_id}&json=1",
                        timeout=30
                    )
                    result_data = result_response.json()
                    
                    if result_data['status'] == 1:
                        return result_data['request']
            
            return None
        except:
            return None
