import sqlite3
import json
import os
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tutor_database.db")

def init_db():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Mastery tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mastery (
            user_id TEXT DEFAULT 'default',
            concept_id TEXT,
            times_explained INTEGER DEFAULT 0,
            times_quizzed INTEGER DEFAULT 0,
            times_taught_back INTEGER DEFAULT 0,
            last_score INTEGER,
            avg_score REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, concept_id)
        )
    ''')
    
    # Learning sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default',
            concept_id TEXT,
            mode TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_mastery(concept_id: str, mastery_data: Dict[str, Any], user_id: str = "default"):
    """Save mastery data to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO mastery 
        (user_id, concept_id, times_explained, times_quizzed, times_taught_back, last_score, avg_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, concept_id,
        mastery_data.get('times_explained', 0),
        mastery_data.get('times_quizzed', 0), 
        mastery_data.get('times_taught_back', 0),
        mastery_data.get('last_score'),
        mastery_data.get('avg_score')
    ))
    
    conn.commit()
    conn.close()

def load_mastery(user_id: str = "default") -> Dict[str, Any]:
    """Load all mastery data from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM mastery WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    
    mastery = {}
    for row in rows:
        concept_id = row[1]
        mastery[concept_id] = {
            'times_explained': row[2],
            'times_quizzed': row[3],
            'times_taught_back': row[4],
            'last_score': row[5],
            'avg_score': row[6]
        }
    
    conn.close()
    return mastery

def log_session(concept_id: str, mode: str, score: int, user_id: str = "default"):
    """Log learning session to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (user_id, concept_id, mode, score)
        VALUES (?, ?, ?, ?)
    ''', (user_id, concept_id, mode, score))
    
    conn.commit()
    conn.close()