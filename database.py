import sqlite3
import logging
from datetime import datetime

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
            visa_type TEXT DEFAULT 'Tourisme / Visite privée - VISE',
            france_visas_ref TEXT,
            first_name TEXT,
            last_name TEXT,
            passport_number TEXT,
            passport_expiry TEXT,
            phone_number TEXT,
            travel_start_date TEXT,
            travel_end_date TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_complete_user(user_data):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (
                email, password, country, group_id, visa_type, france_visas_ref,
                first_name, last_name, passport_number, passport_expiry,
                phone_number, travel_start_date, travel_end_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['email'], user_data['password'], user_data['country'],
            user_data.get('group_id', 'default_group'),
            user_data.get('visa_type', 'Tourisme / Visite privée - VISE'),
            user_data.get('france_visas_ref', ''),
            user_data.get('first_name', ''),
            user_data.get('last_name', ''),
            user_data.get('passport_number', ''),
            user_data.get('passport_expiry', ''),
            user_data.get('phone_number', ''),
            user_data.get('travel_start_date', ''),
            user_data.get('travel_end_date', '')
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_active_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT email, password, country, group_id, visa_type, france_visas_ref,
               first_name, last_name, passport_number, passport_expiry,
               phone_number, travel_start_date, travel_end_date
        FROM users WHERE status = "active"
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return [{
        'email': user[0], 'password': user[1], 'country': user[2],
        'group_id': user[3], 'visa_type': user[4], 'france_visas_ref': user[5],
        'first_name': user[6], 'last_name': user[7], 'passport_number': user[8],
        'passport_expiry': user[9], 'phone_number': user[10],
        'travel_start_date': user[11], 'travel_end_date': user[12]
    } for user in users]
