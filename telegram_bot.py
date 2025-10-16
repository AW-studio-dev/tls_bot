import requests
import time
from config import BOT_TOKEN, ADMIN_CHAT_ID

def send_telegram(message):
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': ADMIN_CHAT_ID, 
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

def notify_booking(user_email, country, reference):
    message = f"""
APPOINTMENT BOOKED!
Email: {user_email}
Country: {country}
Reference: {reference}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    return send_telegram(message)

def notify_slot_found(country):
    message = f"""
SLOT AVAILABLE!
Country: {country}
Attempting to book automatically...
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    return send_telegram(message)

def notify_system_start():
    message = f"""
TLScontact Bot Started
Status: Active and monitoring
Check Interval: 30 seconds
Started: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    return send_telegram(message)

def notify_error(error_message):
    message = f"""
SYSTEM ERROR
Error: {error_message}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    return send_telegram(message)
