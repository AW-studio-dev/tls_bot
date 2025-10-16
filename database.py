import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            country TEXT NOT NULL,
            group_id TEXT,
            visa_type TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO users (email, password, country, visa_type, group_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'aw.studio.dz@gmail.com', 
            '.J7hV/3*6c73a?j', 
            'france', 
            'schengen', 
            'default_group'
        ))
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

def add_tunisian_user(email, password, country, visa_type, group_id=None):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (email, password, country, visa_type, group_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, password, country, visa_type, group_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_active_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT email, password, country, visa_type, group_id FROM users WHERE status = "active"')
    users = cursor.fetchall()
    conn.close()
    
    return [{
        'email': user[0],
        'password': user[1],
        'country': user[2],
        'visa_type': user[3],
        'group_id': user[4]
    } for user in users]
