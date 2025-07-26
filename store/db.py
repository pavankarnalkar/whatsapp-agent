"""SQLite database wrapper for message storage."""

import asyncio
import aiosqlite
from datetime import datetime
from typing import List, Optional, Dict, Any
from config import settings


class MessageDB:
    """SQLite wrapper for storing WhatsApp messages and conversations."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_url.replace("sqlite:///", "")
    
    async def init_db(self):
        """Initialize database with required tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    from_number TEXT NOT NULL,
                    to_number TEXT NOT NULL,
                    message_text TEXT,
                    message_type TEXT DEFAULT 'text',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_from_user BOOLEAN DEFAULT TRUE,
                    urgency_score REAL DEFAULT 0.0,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT UNIQUE NOT NULL,
                    last_message_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    summary TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            await db.commit()
    
    async def store_message(
        self, 
        message_id: str,
        from_number: str,
        to_number: str,
        message_text: str,
        message_type: str = "text",
        is_from_user: bool = True,
        urgency_score: float = 0.0
    ) -> bool:
        """Store a new message in the database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO messages 
                    (message_id, from_number, to_number, message_text, message_type, 
                     is_from_user, urgency_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (message_id, from_number, to_number, message_text, 
                      message_type, is_from_user, urgency_score))
                
                # Update conversation
                await self._update_conversation(db, from_number if is_from_user else to_number)
                await db.commit()
                return True
        except Exception as e:
            print(f"Error storing message: {e}")
            return False
    
    async def _update_conversation(self, db: aiosqlite.Connection, phone_number: str):
        """Update conversation record."""
        await db.execute("""
            INSERT OR REPLACE INTO conversations (phone_number, last_message_time, message_count)
            VALUES (?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT message_count FROM conversations WHERE phone_number = ?), 0) + 1)
        """, (phone_number, phone_number))
    
    async def get_conversation_history(self, phone_number: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages for a phone number."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM messages 
                WHERE from_number = ? OR to_number = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (phone_number, phone_number, limit))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_unprocessed_messages(self) -> List[Dict[str, Any]]:
        """Get messages that haven't been processed yet."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM messages 
                WHERE processed = FALSE AND is_from_user = TRUE
                ORDER BY timestamp ASC
            """)
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def mark_message_processed(self, message_id: str) -> bool:
        """Mark a message as processed."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE messages SET processed = TRUE 
                    WHERE message_id = ?
                """, (message_id,))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error marking message as processed: {e}")
            return False
    
    async def update_conversation_summary(self, phone_number: str, summary: str) -> bool:
        """Update conversation summary."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE conversations SET summary = ? 
                    WHERE phone_number = ?
                """, (summary, phone_number))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating conversation summary: {e}")
            return False


# Global database instance
db = MessageDB()