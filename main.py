import time
import signal
import sys
from database import init_db
from booking_manager import BookingManager
from telegram_bot import notify_error
from telegram_poller import start_telegram_commands
from config import CHECK_INTERVAL

class Application:
    def __init__(self):
        self.booking_manager = BookingManager()
        self.running = True
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        self.running = False
    
    def run(self):
        try:
            init_db()
            start_telegram_commands()
            
            if not self.booking_manager.start_monitoring():
                return
            
            while self.running:
                try:
                    self.booking_manager.process_users()
                    
                    for _ in range(CHECK_INTERVAL):
                        if not self.running:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    notify_error(f"Main loop: {str(e)}")
                    time.sleep(30)
            
        except Exception as e:
            notify_error(f"Critical: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    app = Application()
    app.run()
