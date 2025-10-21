import requests
import sqlite3
import time
from config import BOT_TOKEN, ADMIN_CHAT_ID
from database import add_complete_user

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
            self.send_message(chat_id, "❌ Accès non autorisé")
            return
        
        if text.startswith('/'):
            response = self.process_command(text)
            self.send_message(chat_id, response)
    
    def process_command(self, command):
        command = command.lower()
        
        if command == '/start':
            return "🤖 <b>Bot AI TLS Démarré !</b>\nUtilisez /aide pour les commandes"
        elif command == '/aide':
            return self.show_help()
        elif command == '/utilisateurs':
            return self.list_users()
        elif command == '/statut':
            return self.get_status()
        elif command.startswith('/ajouter'):
            return self.add_user(command)
        elif command.startswith('/supprimer'):
            return self.delete_user(command)
        else:
            return "❌ Commande inconnue. Utilisez /aide"
    
    def add_user(self, command):
        try:
            parts = command.split()
            
            if len(parts) < 4:
                return """❌ Format: /ajouter email motdepasse pays [groupe]
                
📝 <b>Exemple complet:</b>
/ajouter client@email.com MotDePasse123 france groupe_famille

📝 <b>Informations supplémentaires via messages séparés:</b>
• Référence France-Visas
• Prénom et Nom
• Numéro de passeport
• Dates de voyage"""
            
            user_data = {
                'email': parts[1],
                'password': parts[2],
                'country': parts[3],
                'group_id': parts[4] if len(parts) > 4 else 'default_group'
            }
            
            if user_data['country'] not in ['france', 'germany']:
                return "❌ Le pays doit être 'france' ou 'germany'"
            
            success = add_complete_user(user_data)
            
            if success:
                return f"""✅ <b>Utilisateur Ajouté avec Succès !</b>

📧 <b>Email:</b> {user_data['email']}
🇫🇷 <b>Pays:</b> {user_data['country']}
🆔 <b>Groupe:</b> {user_data['group_id']}
🔍 <b>Statut:</b> Surveillance toutes les 30 secondes

💡 <i>Envoyez maintenant les informations supplémentaires séparément.</i>"""
            else:
                return f"❌ L'utilisateur {user_data['email']} existe déjà !"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def list_users(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT email, country, status FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            return " Aucun utilisateur enregistré"
        
        response = " <b>Utilisateurs Enregistrés:</b>\n\n"
        for email, country, status in users:
            status_icon = '✅' if status == 'active' else '❌'
            response += f"{status_icon} <code>{email}</code>\n   🇫🇷 {country}\n\n"
        
        response += f" <b>Total:</b> {len(users)} utilisateurs"
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
                return f"✅ Utilisateur {email} supprimé avec succès"
            else:
                return f"❌ Utilisateur {email} non trouvé"
        except:
            return "❌ Format: /supprimer email@exemple.com"
    
    def get_status(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE status = "active"')
        active_users = cursor.fetchone()[0]
        conn.close()
        
        return f""" <b>Statut du Bot</b>

✅ <b>Système:</b> En fonctionnement
👥 <b>Utilisateurs Actifs:</b> {active_users}
 <b>Intervalle de Vérification:</b> 30 secondes
 <b>Limite de Taux:</b> 3 utilisateurs/minute

Utilisez /utilisateurs pour voir tous les utilisateurs"""
    
    def show_help(self):
        return """
 <b>Commandes Disponibles:</b>

/ajouter email motdepasse pays [groupe]
   ↳ Ajouter un nouvel utilisateur
   <i>Exemple: /ajouter client@email.com MotDePasse123 france famille</i>

/supprimer email
   ↳ Supprimer un utilisateur
   <i>Exemple: /supprimer ancien@email.com</i>

/utilisateurs
   ↳ Lister tous les utilisateurs

/statut
   ↳ Vérifier le statut du bot

/aide
   ↳ Afficher cette aide

💡 <b>Conseils:</b>
• Le pays doit être 'france' ou 'germany'
• Le groupe est optionnel (défaut: 'default_group')
• Le système vérifie toutes les 30 secondes automatiquement
"""
