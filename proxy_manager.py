import requests
import time
import random
from config import BRIGHT_DATA_KEY

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.last_rotation = 0
        self.rotation_interval = 300
        self._initialize_proxies()
        
    def _initialize_proxies(self):
        tunisia_proxy = f"http://{BRIGHT_DATA_KEY}:tn-country-tn@brd.superproxy.io:22225"
        self.proxies.append(tunisia_proxy)
        
        fr_proxy = f"http://{BRIGHT_DATA_KEY}:fr-country-fr@brd.superproxy.io:22225"
        self.proxies.append(fr_proxy)
        
        de_proxy = f"http://{BRIGHT_DATA_KEY}:de-country-de@brd.superproxy.io:22225"
        self.proxies.append(de_proxy)
    
    def get_proxy(self):
        if not self.proxies:
            return None
            
        current_time = time.time()
        if current_time - self.last_rotation > self.rotation_interval and len(self.proxies) > 1:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            self.last_rotation = current_time
            
        proxy_url = self.proxies[self.current_proxy_index]
        return {
            'http': proxy_url,
            'https': proxy_url
        }
