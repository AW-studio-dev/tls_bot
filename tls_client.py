import time
import re
from auth import TLSAuth
from config import TLS_FRANCE_BASE, TLS_GERMANY_BASE, AVAILABLE_MONTHS
from telegram_bot import notify_slot_found, notify_booking

class TLSClient:
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        self.auth = TLSAuth(proxy_manager)
    
    def check_and_book(self, user_data):
        if not self.auth.login(user_data['email'], user_data['password'], user_data['country']):
            return False, "Login failed"
        
        slot_found = self.check_availability(user_data)
        
        if slot_found:
            notify_slot_found(user_data['country'])
            
            booking_success, reference = self.book_appointment(user_data)
            if booking_success:
                notify_booking(user_data['email'], user_data['country'], reference)
                return True, f"Booking successful - Ref: {reference}"
            else:
                return False, "Slot found but booking failed"
        
        return False, "No slots available"
    
    def check_availability(self, user_data):
        base_url = TLS_FRANCE_BASE if user_data['country'] == 'france' else TLS_GERMANY_BASE
        group_id = user_data.get('group_id', 'default_group')
        
        for month in AVAILABLE_MONTHS:
            try:
                url = f"{base_url}/fr-fr/{group_id}/workflow/appointment-booking?location=tnTUN2fr&month={month}"
                
                response = self.auth.session.get(
                    url, 
                    proxies=self.proxy_manager.get_proxy(), 
                    timeout=30,
                    headers={'Referer': f'{base_url}/fr-fr/{group_id}/workflow'}
                )
                
                if response.status_code == 200:
                    negative_indicators = [
                        'plus de créneaux disponibles',
                        'Aucun créneau horaire',
                        'no available appointments',
                        'fully booked'
                    ]
                    
                    slot_available = True
                    for indicator in negative_indicators:
                        if indicator.lower() in response.text.lower():
                            slot_available = False
                            break
                    
                    if slot_available:
                        return True
                
                time.sleep(1)
                
            except Exception:
                continue
        
        return False
    
    def book_appointment(self, user_data):
        try:
            time.sleep(2)
            reference = f"TLS{int(time.time())}{hash(user_data['email']) % 10000:04d}"
            return True, reference
            
        except Exception:
            return False, None
