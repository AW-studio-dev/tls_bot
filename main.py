import time
import signal
import sys
import os
from database import init_db
from booking_manager import BookingManager
from telegram_bot import notify_error
from telegram_poller import start_telegram_commands
from config import CHECK_INTERVAL

# Railway platform detection
if os.environ.get('RAILWAY_ENVIRONMENT'):
    print(" Running on Railway platform")
    # Additional Railway-specific setup if needed

class Application:
    def __init__(self):
        self.booking_manager = BookingManager()
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n Arrêt du système demandé...")
        self.running = False
        self.booking_manager.cleanup()
    
    def run(self):
        try:
            # Initialize database
            print(" Initialisation de la base de données...")
            init_db()
            
            # Start Telegram command handler
            print(" Démarrage du gestionnaire Telegram...")
            start_telegram_commands()
            
            # Start the booking manager
            print(" Démarrage du gestionnaire de réservation...")
            if not self.booking_manager.start_monitoring():
                print("❌ Échec du démarrage du gestionnaire de réservation")
                return
            
            print("✅ Système AI TLS Bot démarré avec succès!")
            print(" Surveillance active - Vérification toutes les 30 secondes")
            print("👥 Utilisateurs en cours de surveillance...")
            
            # Main monitoring loop
            while self.running:
                try:
                    self.booking_manager.process_users()
                    
                    # Wait for next check interval
                    for _ in range(CHECK_INTERVAL):
                        if not self.running:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    print(f" Erreur dans la boucle principale: {e}")
                    notify_error(f"Boucle principale: {str(e)}")
                    time.sleep(30)  # Wait before retrying
            
            print("✅ Arrêt du système terminé avec succès")
            
        except Exception as e:
            print(f" Erreur critique: {e}")
            notify_error(f"Erreur critique: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print(" BOT AI TLS CONTACT - DÉMARRAGE")
    print("=" * 50)
    
    app = Application()
    app.run()
