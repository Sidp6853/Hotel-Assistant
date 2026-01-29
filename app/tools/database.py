"""
Database initialization and query utilities
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


def initialize_database(db_path: Path = settings.DB_PATH):
    """
    Create the complaints database and tables
    
    Args:
        db_path: Path to SQLite database file
    """
    try:
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id TEXT PRIMARY KEY,
            guest_name TEXT,
            room_number TEXT,
            contact_info TEXT,
            complaint_text TEXT,
            severity_level TEXT,
            category TEXT,
            sentiment_score REAL,
            escalation_required INTEGER,
            key_issues TEXT,
            summary_reasoning TEXT,
            internal_actions TEXT,
            assigned_department TEXT,
            estimated_resolution_time TEXT,
            guest_response TEXT,
            recurring_guest INTEGER,
            recurring_room_issue INTEGER,
            stored_successfully INTEGER,
            created_at TEXT
        )
        """)

        conn.commit()
        conn.close()
        
        logger.info(f"✅ Database initialized at {db_path}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


def get_guest_history(guest_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve complaint history for a specific guest
    
    Args:
        guest_name: Name of the guest
        limit: Maximum number of records to return
        
    Returns:
        List of complaint records
    """
    try:
        conn = sqlite3.connect(str(settings.DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        results = cur.execute("""
            SELECT category, severity_level, created_at 
            FROM complaints 
            WHERE guest_name=? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (guest_name, limit)).fetchall()
        
        conn.close()
        
        return [dict(row) for row in results]
        
    except Exception as e:
        logger.error(f"Failed to retrieve guest history: {e}")
        return []


def get_room_history(room_number: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve complaint history for a specific room
    
    Args:
        room_number: Room number
        limit: Maximum number of records to return
        
    Returns:
        List of complaint records
    """
    try:
        conn = sqlite3.connect(str(settings.DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        results = cur.execute("""
            SELECT category, severity_level, created_at 
            FROM complaints 
            WHERE room_number=? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (room_number, limit)).fetchall()
        
        conn.close()
        
        return [dict(row) for row in results]
        
    except Exception as e:
        logger.error(f"Failed to retrieve room history: {e}")
        return []