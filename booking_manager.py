import time
import logging
from database import get_active_users
from ai_automation import AIAutomation
from telegram_bot import notify_system_start, notify_error, notify_booking, notify_slot_found
from config import CHECK_INTERVAL, MAX_USERS_PER_MINUTE, REQUEST_DELAY

logging.basicConfig(level=logging.INFO)

class BookingManager:
    def __init__(self):
        self.automation = AIAutomation(headless=True)
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
                success, message = self.process_user_booking(user)
                
                if success:
                    logging.info(f"Booking successful for {user['email']}")
                else:
                    logging.info(f"Booking attempt: {user['email']} - {message}")
                
                self.users_processed_this_minute += 1
                self.total_checks += 1
                
                if i < users_to_process - 1:
                    time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                logging.error(f"Error processing {user['email']}: {e}")
                continue
    
    def process_user_booking(self, user_data):
        try:
            if not self.automation.smart_login(user_data['email'], user_data['password'], user_data['country']):
                return False, "Échec de la connexion"
            
            if not self.automation.navigate_to_booking(user_data.get('group_id', 'default_group')):
                return False, "Navigation échouée"
            
            slot_available = self.automation.check_availability()
            
            if slot_available:
                notify_slot_found(user_data['country'])
                
                if self.automation.complete_application_form(user_data):
                    booking_success = self.automation.smart_book_appointment()
                    if booking_success:
                        reference = f"TLS{int(time.time())}{hash(user_data['email']) % 10000:04d}"
                        notify_booking(user_data['email'], user_data['country'], reference)
                        return True, f"Réservation réussie - Réf: {reference}"
                    else:
                        return False, "Créneau trouvé mais réservation échouée"
                else:
                    return False, "Échec du formulaire de demande"
            
            return False, "Aucun créneau disponible"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def start_monitoring(self):
        logging.info("Démarrage du système AI TLS Bot...")
        notify_system_start()
        return True
    
    def cleanup(self):
        self.automation.close()
