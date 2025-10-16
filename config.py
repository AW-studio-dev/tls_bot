import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = '8492137210:AAEPE77aov1kzG7EZ5E7KmZxGrxBiOIumxU'
ADMIN_CHAT_ID = '5991222987'

TLS_FRANCE_BASE = 'https://visas-fr.tlscontact.com/fr-fr/country/tn/vac/tnTUN2fr'
TLS_GERMANY_BASE = 'https://visas-de.tlscontact.com/fr-fr/country/tn/vac/tnTUN2de'

BRIGHT_DATA_KEY = '6b2d4ea83e046d009eca4f82498535bc6e9c2b064da83f94a8e9103c1fe03b87'
TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY', 'PLACE-HOLDER-2CAPTCHA-KEY')

DB_FILE = 'users.db'
CHECK_INTERVAL = 30
MAX_USERS_PER_MINUTE = 3
REQUEST_DELAY = 2

ACTIVE_ACCOUNT = {
    'email': 'aw.studio.dz@gmail.com',
    'password': '.J7hV/3*6c73a?j',
    'country': 'france',
    'group_id': 'default_group'
}

AVAILABLE_MONTHS = ['10-2025', '11-2025', '12-2025']
