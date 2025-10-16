import requests
import sqlite3
import time
from config import BOT_TOKEN, ADMIN_CHAT_ID
from database import add_tunisian_user

class TelegramCommandHandler:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.admin_chat_id = ADMIN_CHAT_ID
        
    def send_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        try:
            requests.post(url, data=payload, timeout=10)
            return True
        except:
            return False
    
    def handle_message(self, message_data):
        chat_id = message_data['chat']['id']
        text = message_data.get('text', '').strip()
        
        if str(chat_id) != self.admin_chat_id:
            self.send_message(chat_id, "Unauthorized access")
            return
        
        if text.startswith('/'):
            response = self.process_command(text)
            self.send_message(chat_id, response)
    
    def process_command(self, command):
        command = command.lower()
        
        if command == '/start':
            return "TLS Bot Started! Use /help for commands"
        elif command == '/help':
            return self.show_help()
        elif command == '/users':
            return self.list_users()
        elif command == '/status':
            return self.get_status()
        elif command.startswith('/adduser'):
            return self.add_user(command)
        elif command.startswith('/delete'):
            return self.delete_user(command)
        else:
            return "Unknown command. Use /help"
    
    def add_user(self, command):
        try:
            parts = command.split()
            
            if len(parts) < 4:
                return "Format: /adduser email password country [group]"
            
            email = parts[1]
            password = parts[2]
            country = parts[3]
            group_id = parts[4] if len(parts) > 4 else 'default_group'
            
            if country not in ['france', 'germany']:
                return "Country must be 'france' or 'germany'"
            
            success = add_tunisian_user(email, password, country, 'schengen', group_id)
            
            if success:
                return f"User Added Successfully! Now monitoring every 30 seconds."
            else:
                return f"User {email} already exists!"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def list_users(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT email, country, status FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            return "No users registered yet"
        
        response = "Registered Users:"
        for email, country, status in users:
            status_icon = '✔' if status == 'active' else '✘'
            response += f"\n{status_icon} {email} ({country})"
        
        response += f"\n\nTotal: {len(users)} users"
        return response
    
    def delete_user(self, command):
        try:
            email = command.split()[1]
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE email = ?', (email,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            
            if deleted:
                return f"User {email} deleted successfully"
            else:
                return f"User {email} not found"
        except:
            return "Format: /delete email@example.com"
    
    def get_status(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE status = "active"')
        active_users = cursor.fetchone()[0]
        conn.close()
        
        return f"Bot Status: Running | Active Users: {active_users} | Check Interval: 30 seconds"
    
    def show_help(self):
        return """
Available Commands:

/adduser email password country [group]
   Add new monitoring user

/delete email
   Remove a user

/users
   List all registered users

/status
   Check bot status

/help
   Show this help
"""
