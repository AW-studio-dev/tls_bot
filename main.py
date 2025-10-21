import time
import signal
import sys
import platform
from database import init_db
from booking_manager import BookingManager
from telegram_bot import notify_error
from telegram_poller import start_telegram_commands
from config import CHECK_INTERVAL

# إعداد Tesseract للويندوز
def setup_tesseract():
    if platform.system() == "Windows":
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            print("✅ Tesseract configuré pour Windows")
        except Exception as e:
            print(f"⚠️  Attention Tesseract: {e}")
            print("📝 Veuillez installer Tesseract OCR depuis:")
            print("🔗 https://github.com/UB-Mannheim/tesseract/wiki")

class Application:
    def __init__(self):
        self.booking_manager = BookingManager()
        self.running = True
        
        # إعداد معالجات الإشارات للإغلاق الآمن
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n🛑 Arrêt du système en cours...")
        self.running = False
        self.booking_manager.cleanup()
        sys.exit(0)
    
    def run(self):
        try:
            print("🚀 Démarrage du Bot AI TLS...")
            
            # إعداد Tesseract أولاً
            setup_tesseract()
            
            # تهيئة قاعدة البيانات
            print("📀 Initialisation de la base de données...")
            init_db()
            
            # بدء نظام الأوامر في التليجرام
            print("🤖 Démarrage du système de commandes Telegram...")
            start_telegram_commands()
            
            # بدء المراقبة
            print("🔍 Démarrage du système de surveillance...")
            if not self.booking_manager.start_monitoring():
                print("❌ Échec du démarrage de la surveillance")
                return
            
            print("=" * 50)
            print("🤖 Système AI TLS Bot démarré avec succès!")
            print("📊 Surveillance active toutes les 30 secondes")
            print("💬 Utilisez Telegram pour contrôler le système")
            print("🛑 Ctrl+C pour arrêter le système")
            print("=" * 50)
            
            # الحلقة الرئيسية
            while self.running:
                try:
                    # معالجة المستخدمين
                    self.booking_manager.process_users()
                    
                    # انتظار بين الدورات
                    for i in range(CHECK_INTERVAL):
                        if not self.running:
                            break
                        time.sleep(1)
                        
                except KeyboardInterrupt:
                    print("\n🛑 Arrêt demandé par l'utilisateur...")
                    self.running = False
                    break
                    
                except Exception as e:
                    print(f"⚠️  Erreur dans la boucle principale: {e}")
                    try:
                        notify_error(f"Boucle principale: {str(e)}")
                    except:
                        pass
                    time.sleep(30)
            
            print("✅ Arrêt du système terminé avec succès!")
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
            
        except Exception as e:
            print(f"💥 Erreur critique: {e}")
            try:
                notify_error(f"Erreur critique: {str(e)}")
            except:
                pass
            sys.exit(1)

if __name__ == "__main__":
    app = Application()
    app.run()
