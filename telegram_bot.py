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
✅ <b>RENDEZ-VOUS RÉSERVÉ !</b>

 <b>Email:</b> {user_email}
🇫🇷 <b>Pays:</b> {country}
 <b>Référence:</b> <code>{reference}</code>
 <b>Heure:</b> {time.strftime('%d/%m/%Y %H:%M:%S')}

La réservation a été effectuée avec succès !
"""
    return send_telegram(message)

def notify_slot_found(country):
    message = f"""
🚨 <b>CRÉNEAU DISPONIBLE !</b>

🇫🇷 <b>Pays:</b> {country}
 <b>Tentative de réservation automatique...</b>
 <b>Heure:</b> {time.strftime('%d/%m/%Y %H:%M:%S')}
"""
    return send_telegram(message)

def notify_system_start():
    message = f"""
 <b>BOT TLS DÉMARRÉ</b>

✅ <b>Statut:</b> Actif et surveillance
 <b>Intervalle de vérification:</b> 30 secondes
👥 <b>Utilisateurs actifs:</b> Surveillance en cours
 <b>Démarrage:</b> {time.strftime('%d/%m/%Y %H:%M:%S')}

Le système surveille maintenant les créneaux disponibles.
"""
    return send_telegram(message)

def notify_error(error_message):
    message = f"""
❌ <b>ERREUR SYSTÈME</b>

 <b>Erreur:</b> <code>{error_message}</code>
 <b>Heure:</b> {time.strftime('%d/%m/%Y %H:%M:%S')}
"""
    return send_telegram(message)
