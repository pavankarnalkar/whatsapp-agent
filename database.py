import sqlite3
import os
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database and create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatsapp_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                message_body TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message_sid TEXT,
                profile_name TEXT,
                from_number TEXT,
                to_number TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_message(self, sender, message_body, timestamp, message_sid=None, 
                   profile_name=None, from_number=None, to_number=None):
        """Log a WhatsApp message to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO whatsapp_messages 
            (sender, message_body, timestamp, message_sid, profile_name, from_number, to_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sender, message_body, timestamp, message_sid, profile_name, from_number, to_number))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return message_id
    
    def get_messages(self, limit=50):
        """Retrieve recent messages from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM whatsapp_messages 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return messages