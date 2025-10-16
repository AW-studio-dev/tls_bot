import time
import logging
from database import get_active_users
from tls_client import TLSClient
from proxy_manager import ProxyManager
from telegram_bot import notify_system_start, notify_error
from config import CHECK_INTERVAL, MAX_USERS_PER_MINUTE, REQUEST_DELAY

logging.basicConfig(level=logging.INFO)

class BookingManager:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.tls_client = TLSClient(self.proxy_manager)
        self.users_processed_this_minute = 0
        self.last_minute_reset = time.time()
        self.total_checks = 0
        
    def process_users(self):
        current_time = time.time()
        
        if current_time - self.last_minute_reset > 60:
            self.users_processed_this_minute = 0
            self.last_minute_reset = current_time
        
        users = get_active_users()
        if not users:
            return
        
        available_slots = MAX_USERS_PER_MINUTE - self.users_processed_this_minute
        users_to_process = min(available_slots, len(users))
        
        if users_to_process == 0:
            return
        
        for i in range(users_to_process):
            user = users[i]
            try:
                success, message = self.tls_client.check_and_book(user)
                self.users_processed_this_minute += 1
                self.total_checks += 1
                
                if i < users_to_process - 1:
                    time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                continue
    
    def start_monitoring(self):
        if not self.proxy_manager.test_proxy_connectivity():
            notify_error("Proxy connectivity test failed")
            return False
        
        notify_system_start()
        return True
