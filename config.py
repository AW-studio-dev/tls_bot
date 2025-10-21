import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = 'replace'
ADMIN_CHAT_ID = 'replace'

TLS_FRANCE_BASE = 'https://visas-fr.tlscontact.com'
TLS_GERMANY_BASE = 'https://visas-de.tlscontact.com'

BRIGHT_DATA_KEY = '6b2d4ea83e046d009eca4f82498535bc6e9c2b064da83f94a8e9103c1fe03b87'
TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY', '')

DB_FILE = 'users.db'
CHECK_INTERVAL = 30
MAX_USERS_PER_MINUTE = 3
REQUEST_DELAY = 2

AVAILABLE_MONTHS = ['10-2025', '11-2025', '12-2025']
