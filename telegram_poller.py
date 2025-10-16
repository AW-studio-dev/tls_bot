import requests
import time
import threading
from config import BOT_TOKEN
from telegram_commands import TelegramCommandHandler

class TelegramPoller:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.handler = TelegramCommandHandler()
        self.last_update_id = 0
        
    def get_updates(self):
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {'offset': self.last_update_id + 1, 'timeout': 30}
        
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data['ok'] and data['result']:
                    for update in data['result']:
                        self.last_update_id = update['update_id']
                        if 'message' in update:
                            self.handler.handle_message(update['message'])
        except Exception:
            pass
    
    def start_polling(self):
        while True:
            self.get_updates()
            time.sleep(1)

def start_telegram_commands():
    poller = TelegramPoller()
    poller.start_polling()

telegram_thread = threading.Thread(target=start_telegram_commands, daemon=True)
telegram_thread.start()
