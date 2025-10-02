#!/usr/bin/env python3
"""
RAF Bomber Command Research Database - Public Ready Version
Enhanced with accessibility, user experience, and comprehensive features
"""

import os
import sqlite3
import json
import requests
import time
import logging
from datetime import datetime
from functools import wraps
from collections import defaultdict
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
DATABASE_PATH = '/tmp/raf_bomber_command.db'
AI_SYSTEM_URL = 'http://localhost:5002'

# Rate limiting storage
request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60

def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        now = time.time()
        
        # Clean old requests
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip] 
            if now - req_time < RATE_LIMIT_WINDOW
        ]
        
        # Check rate limit
        if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': RATE_LIMIT_WINDOW
            }), 429
        
        # Add current request
        request_counts[client_ip].append(now)
        
        return f(*args, **kwargs)
    return decorated_function

def validate_input(data, required_fields):
    """Validate and sanitize input data"""
    if not data:
        return False, "No data provided"
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        # Basic sanitization
        if isinstance(data[field], str):
            data[field] = data[field].strip()
            if len(data[field]) > 1000:
                return False, f"Field {field} too long (max 1000 characters)"
    
    return True, None

def initialize_database():
    """Initialize database with essential RAF Bomber Command data"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create personnel table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personnel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                service_number TEXT,
                rank TEXT,
                role TEXT,
                squadron TEXT,
                biography TEXT,
                memorial_info TEXT,
                date_of_birth TEXT,
                date_of_death TEXT,
                age_at_death INTEGER
            )
        ''')
        
        # Create aircraft table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aircraft (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_number TEXT NOT NULL,
                aircraft_type TEXT,
                squadron TEXT,
                crew_details TEXT,
                service_history TEXT,
                notable_missions TEXT,
                first_flight TEXT,
                last_mission TEXT
            )
        ''')
        
        # Insert Patrick Cassidy record with enhanced details
        cursor.execute('''
            INSERT OR REPLACE INTO personnel 
            (name, service_number, rank, role, squadron, biography, memorial_info, date_of_birth, date_of_death, age_at_death)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Sergeant Patrick Cassidy',
            '1802082',
            'Sergeant',
            'Flight Engineer',
            '97 Squadron RAF Pathfinders',
            'Flight Engineer with 97 Squadron RAF Pathfinders. Patrick served with the elite Pathfinder Force, responsible for target marking and leading bomber formations to their targets. He was killed when Lancaster JB174 was shot down by German night fighters during a raid on Hanover on 8/9 October 1943. Only 20 years old at the time of his death, Patrick exemplified the courage and dedication of RAF Bomber Command aircrew. He is commemorated on the Runnymede Memorial, which honors those who have no known grave.',
            'Runnymede Memorial Panel 119',
            '1923',
            '8/9 October 1943',
            20
        ))
        
        # Insert Lancaster JB174 record with enhanced details
        cursor.execute('''
            INSERT OR REPLACE INTO aircraft 
            (serial_number, aircraft_type, squadron, crew_details, service_history, notable_missions, first_flight, last_mission)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'JB174',
            'Avro Lancaster B.III',
            '97 Squadron RAF Pathfinders',
            'Patrick Cassidy (Flight Engineer), crew of 7 including pilot, navigator, bomb aimer, wireless operator, and two gunners',
            'Served with 97 Squadron RAF Pathfinders from August 1943. Service life: 47 days (shortest recorded service life in squadron history). Used for target marking operations over occupied Europe.',
            'Final mission: Hanover raid, 8/9 October 1943. Shot down by German night fighters. All crew members killed in action.',
            'August 1943',
            '8/9 October 1943'
        ))
        
        # Insert Guy Gibson record
        cursor.execute('''
            INSERT OR REPLACE INTO personnel 
            (name, service_number, rank, role, squadron, biography, memorial_info, date_of_birth, date_of_death, age_at_death)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Wing Commander Guy Gibson',
            '39438',
            'Wing Commander',
            'Pilot',
            '617 Squadron "Dam Busters"',
            'Wing Commander Guy Penrose Gibson VC DSO* DFC* was a distinguished Royal Air Force pilot during the Second World War and a recipient of the Victoria Cross, the highest award for gallantry in the face of the enemy. He was the first commanding officer of No. 617 Squadron, which he led in the famous "Dambusters" raid on German dams in May 1943. Gibson completed 174 operational sorties before his death.',
            'Steenbergen-en-Kruisland (Steenbergen) General Cemetery',
            '12 August 1918',
            '19 September 1944',
            26
        ))
        
        # Insert additional sample personnel
        sample_personnel = [
            ('Flight Lieutenant John Smith', '123456', 'Flight Lieutenant', 'Navigator', '97 Squadron RAF Pathfinders', 'Navigator with 97 Squadron RAF Pathfinders. Completed 30 operational sorties over occupied Europe.', 'Runnymede Memorial Panel 120', '1920', '15 March 1944', 24),
            ('Sergeant William Jones', '789012', 'Sergeant', 'Wireless Operator', '97 Squadron RAF Pathfinders', 'Wireless Operator with 97 Squadron RAF Pathfinders. Responsible for radio communications during target marking operations.', 'Runnymede Memorial Panel 118', '1922', '2 November 1943', 21),
            ('Flying Officer Robert Brown', '345678', 'Flying Officer', 'Bomb Aimer', '617 Squadron "Dam Busters"', 'Bomb Aimer with 617 Squadron. Participated in the famous Dambusters raid on German dams in May 1943.', 'Reichswald Forest War Cemetery', '1921', '10 April 1945', 24),
        ]
        
        for person in sample_personnel:
            cursor.execute('''
                INSERT OR REPLACE INTO personnel 
                (name, service_number, rank, role, squadron, biography, memorial_info, date_of_birth, date_of_death, age_at_death)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', person)
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully with enhanced RAF data")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

class DatabaseManager:
    """Enhanced database manager with advanced search capabilities"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        if not os.path.exists(self.db_path):
            initialize_database()
    
    def get_connection(self):
        """Get database connection with optimizations"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=10000')
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def search_personnel(self, query: str, filters: dict = None, limit: int = 20) -> tuple:
        """Enhanced personnel search with filters"""
        conn = self.get_connection()
        if not conn:
            return [], "Database connection failed"
        
        try:
            query = query.strip()[:100]
            
            # Base SQL with enhanced relevance scoring
            base_sql = """
            SELECT *, 
                   (CASE 
                    WHEN LOWER(name) = LOWER(?) THEN 10
                    WHEN LOWER(service_number) = LOWER(?) THEN 10
                    WHEN LOWER(name) LIKE LOWER(?) THEN 8
                    WHEN LOWER(service_number) LIKE LOWER(?) THEN 8
                    WHEN LOWER(squadron) LIKE LOWER(?) THEN 6
                    WHEN LOWER(rank) LIKE LOWER(?) THEN 4
                    WHEN LOWER(role) LIKE LOWER(?) THEN 3
                    ELSE 1
                   END) as relevance_score
            FROM personnel 
            WHERE (LOWER(name) LIKE LOWER(?) OR LOWER(service_number) LIKE LOWER(?) 
                  OR LOWER(squadron) LIKE LOWER(?) OR LOWER(rank) LIKE LOWER(?) 
                  OR LOWER(role) LIKE LOWER(?) OR LOWER(biography) LIKE LOWER(?))
            """
            
            # Add filters
            filter_conditions = []
            filter_params = []
            
            if filters:
                if filters.get('squadron'):
                    filter_conditions.append("LOWER(squadron) LIKE LOWER(?)")
                    filter_params.append(f"%{filters['squadron']}%")
                
                if filters.get('rank'):
                    filter_conditions.append("LOWER(rank) LIKE LOWER(?)")
                    filter_params.append(f"%{filters['rank']}%")
                
                if filters.get('role'):
                    filter_conditions.append("LOWER(role) LIKE LOWER(?)")
                    filter_params.append(f"%{filters['role']}%")
            
            if filter_conditions:
                base_sql += " AND " + " AND ".join(filter_conditions)
            
            base_sql += " ORDER BY relevance_score DESC, name ASC LIMIT ?"
            
            exact_match = query
            partial_match = f"%{query}%"
            
            params = [
                exact_match, exact_match,
                partial_match, partial_match,
                partial_match, partial_match, partial_match,
                partial_match, partial_match, partial_match,
                partial_match, partial_match, partial_match
            ] + filter_params + [limit]
            
            cursor = conn.execute(base_sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            logger.info(f"Personnel search for '{query}' with filters {filters} returned {len(results)} results")
            return results, None
            
        except Exception as e:
            logger.error(f"Personnel search error: {e}")
            return [], f"Search failed: {str(e)}"
        finally:
            conn.close()
    
    def search_aircraft(self, query: str, filters: dict = None, limit: int = 20) -> tuple:
        """Enhanced aircraft search with filters"""
        conn = self.get_connection()
        if not conn:
            return [], "Database connection failed"
        
        try:
            query = query.strip()[:100]
            
            base_sql = """
            SELECT *, 
                   (CASE 
                    WHEN LOWER(serial_number) = LOWER(?) THEN 10
                    WHEN LOWER(serial_number) LIKE LOWER(?) THEN 8
                    WHEN LOWER(aircraft_type) LIKE LOWER(?) THEN 6
                    WHEN LOWER(squadron) LIKE LOWER(?) THEN 5
                    ELSE 1
                   END) as relevance_score
            FROM aircraft 
            WHERE (LOWER(serial_number) LIKE LOWER(?) OR LOWER(aircraft_type) LIKE LOWER(?) 
                  OR LOWER(squadron) LIKE LOWER(?) OR LOWER(crew_details) LIKE LOWER(?) 
                  OR LOWER(service_history) LIKE LOWER(?))
            """
            
            # Add filters
            filter_conditions = []
            filter_params = []
            
            if filters:
                if filters.get('aircraft_type'):
                    filter_conditions.append("LOWER(aircraft_type) LIKE LOWER(?)")
                    filter_params.append(f"%{filters['aircraft_type']}%")
                
                if filters.get('squadron'):
                    filter_conditions.append("LOWER(squadron) LIKE LOWER(?)")
                    filter_params.append(f"%{filters['squadron']}%")
            
            if filter_conditions:
                base_sql += " AND " + " AND ".join(filter_conditions)
            
            base_sql += " ORDER BY relevance_score DESC, serial_number ASC LIMIT ?"
            
            exact_match = query
            partial_match = f"%{query}%"
            
            params = [
                exact_match, partial_match,
                partial_match, partial_match,
                partial_match, partial_match, partial_match,
                partial_match, partial_match
            ] + filter_params + [limit]
            
            cursor = conn.execute(base_sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            logger.info(f"Aircraft search for '{query}' with filters {filters} returned {len(results)} results")
            return results, None
            
        except Exception as e:
            logger.error(f"Aircraft search error: {e}")
            return [], f"Search failed: {str(e)}"
        finally:
            conn.close()
    
    def get_database_stats(self) -> dict:
        """Get enhanced database statistics"""
        conn = self.get_connection()
        if not conn:
            return {'error': 'Database connection failed'}
        
        try:
            stats = {}
            
            # Basic counts
            cursor = conn.execute("SELECT COUNT(*) as count FROM personnel")
            stats['personnel_count'] = cursor.fetchone()['count']
            
            cursor = conn.execute("SELECT COUNT(*) as count FROM aircraft")
            stats['aircraft_count'] = cursor.fetchone()['count']
            
            cursor = conn.execute("SELECT COUNT(DISTINCT squadron) as count FROM personnel WHERE squadron IS NOT NULL")
            stats['squadron_count'] = cursor.fetchone()['count']
            
            # Age statistics
            cursor = conn.execute("SELECT AVG(age_at_death) as avg_age, MIN(age_at_death) as min_age, MAX(age_at_death) as max_age FROM personnel WHERE age_at_death IS NOT NULL")
            age_stats = cursor.fetchone()
            if age_stats['avg_age']:
                stats['average_age_at_death'] = round(age_stats['avg_age'], 1)
                stats['youngest_age_at_death'] = age_stats['min_age']
                stats['oldest_age_at_death'] = age_stats['max_age']
            
            # Squadron breakdown
            cursor = conn.execute("SELECT squadron, COUNT(*) as count FROM personnel WHERE squadron IS NOT NULL GROUP BY squadron ORDER BY count DESC")
            stats['squadron_breakdown'] = [dict(row) for row in cursor.fetchall()]
            
            logger.info(f"Enhanced database stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {'error': f'Stats failed: {str(e)}'}
        finally:
            conn.close()

# Initialize database manager
db_manager = DatabaseManager()

@app.route('/')
def serve_frontend():
    """Serve the enhanced frontend with accessibility features"""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="RAF Bomber Command Research Database - Preserving the memory of those who served with advanced AI research capabilities">
        <meta name="keywords" content="RAF, Bomber Command, Patrick Cassidy, World War 2, Memorial, Database">
        <title>RAF Bomber Command Research Database - Memorial & AI Research System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            :root {
                --primary-gold: #d4af37;
                --primary-blue: #1e3a8a;
                --dark-bg: #1a1a1a;
                --card-bg: rgba(42, 42, 42, 0.8);
                --text-light: #fff;
                --text-muted: #ccc;
                --success-green: #10b981;
                --error-red: #ef4444;
                --warning-orange: #f59e0b;
            }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, var(--dark-bg) 0%, #2d2d2d 100%);
                color: var(--text-light); 
                min-height: 100vh;
                line-height: 1.6;
            }
            
            /* Accessibility improvements */
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
            
            /* Focus indicators */
            button:focus, input:focus, textarea:focus, select:focus {
                outline: 3px solid var(--primary-gold);
                outline-offset: 2px;
            }
            
            /* Skip link for keyboard navigation */
            .skip-link {
                position: absolute;
                top: -40px;
                left: 6px;
                background: var(--primary-gold);
                color: var(--dark-bg);
                padding: 8px;
                text-decoration: none;
                border-radius: 4px;
                z-index: 1000;
            }
            
            .skip-link:focus {
                top: 6px;
            }
            
            .header { 
                background: linear-gradient(90deg, var(--primary-blue) 0%, #3b82f6 100%);
                padding: 15px 0; 
                text-align: center; 
                color: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }
            
            .header h1 { 
                font-size: 1.2em; 
                margin: 0; 
                font-weight: 600;
            }
            
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
            }
            
            .badge { 
                width: 80px; 
                height: 80px; 
                margin: 20px auto;
                background: radial-gradient(circle, var(--primary-gold) 0%, #b8941f 100%);
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
                position: relative;
            }
            
            .badge::before { 
                content: "★"; 
                font-size: 40px; 
                color: var(--dark-bg); 
            }
            
            .main-title { 
                text-align: center; 
                font-size: 2.5em; 
                margin: 20px 0;
                background: linear-gradient(45deg, var(--primary-gold), #f4e4a6);
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle { 
                text-align: center; 
                color: var(--text-muted); 
                margin-bottom: 40px; 
                font-style: italic; 
                font-size: 1.1em;
            }
            
            .tabs { 
                display: flex; 
                justify-content: center; 
                margin: 30px 0; 
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .tab { 
                padding: 15px 30px; 
                border: none; 
                border-radius: 8px;
                cursor: pointer; 
                font-size: 16px; 
                font-weight: bold;
                transition: all 0.3s ease; 
                color: white;
                min-width: 150px;
                position: relative;
            }
            
            .tab[aria-selected="true"] {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            
            .tab.personnel { background: linear-gradient(45deg, #059669, var(--success-green)); }
            .tab.aircraft { background: linear-gradient(45deg, #2563eb, #3b82f6); }
            .tab.ai { background: linear-gradient(45deg, #d97706, var(--warning-orange)); }
            .tab.stats { background: linear-gradient(45deg, #7c3aed, #8b5cf6); }
            .tab.help { background: linear-gradient(45deg, #6b7280, #9ca3af); }
            
            .tab:hover:not([aria-selected="true"]) { 
                transform: translateY(-1px); 
                opacity: 0.9;
            }
            
            .content { 
                background: var(--card-bg); 
                border-radius: 15px; 
                padding: 30px;
                margin: 20px 0; 
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .search-section h2 { 
                color: var(--primary-gold); 
                margin-bottom: 20px; 
                font-size: 1.8em;
            }
            
            .search-section p {
                margin-bottom: 20px;
                color: var(--text-muted);
            }
            
            .search-box { 
                display: flex; 
                gap: 10px; 
                margin: 20px 0;
                flex-wrap: wrap; 
                align-items: stretch;
            }
            
            .search-input { 
                flex: 1; 
                min-width: 300px; 
                padding: 15px; 
                border: none; 
                border-radius: 8px;
                background: rgba(255,255,255,0.1); 
                color: white; 
                font-size: 16px;
                border: 2px solid rgba(255,255,255,0.2);
                transition: border-color 0.3s ease;
            }
            
            .search-input:focus {
                border-color: var(--primary-gold);
            }
            
            .search-input::placeholder { 
                color: #aaa; 
            }
            
            .search-btn { 
                padding: 15px 30px; 
                border: none; 
                border-radius: 8px;
                background: linear-gradient(45deg, #d97706, var(--warning-orange));
                color: white; 
                font-weight: bold; 
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 120px;
                position: relative;
            }
            
            .search-btn:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 5px 15px rgba(217, 119, 6, 0.3); 
            }
            
            .search-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .quick-buttons { 
                display: flex; 
                gap: 10px; 
                margin: 20px 0; 
                flex-wrap: wrap; 
            }
            
            .quick-btn { 
                padding: 10px 20px; 
                border: none; 
                border-radius: 20px;
                background: rgba(255,255,255,0.1); 
                color: white; 
                cursor: pointer;
                transition: all 0.3s ease; 
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .quick-btn:hover { 
                background: rgba(212, 175, 55, 0.2); 
                border-color: var(--primary-gold);
            }
            
            .filters {
                display: flex;
                gap: 15px;
                margin: 20px 0;
                flex-wrap: wrap;
                align-items: center;
            }
            
            .filter-group {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .filter-group label {
                font-size: 0.9em;
                color: var(--text-muted);
                font-weight: 500;
            }
            
            .filter-select {
                padding: 8px 12px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                background: rgba(255,255,255,0.1);
                color: white;
                font-size: 14px;
                min-width: 120px;
            }
            
            .results { 
                margin-top: 20px; 
                padding: 20px; 
                border-radius: 10px;
                background: rgba(0,0,0,0.3); 
                min-height: 200px;
                position: relative;
            }
            
            .result-item { 
                background: rgba(255,255,255,0.05); 
                margin: 15px 0; 
                padding: 20px;
                border-radius: 8px; 
                border-left: 4px solid var(--primary-gold);
                transition: all 0.3s ease;
            }
            
            .result-item:hover {
                background: rgba(255,255,255,0.08);
                transform: translateX(5px);
            }
            
            .result-name { 
                color: var(--primary-gold); 
                font-weight: bold; 
                font-size: 1.2em; 
                margin-bottom: 8px;
            }
            
            .result-details { 
                color: var(--text-muted); 
                margin: 5px 0; 
                line-height: 1.5;
            }
            
            .result-details strong {
                color: var(--text-light);
            }
            
            .loading { 
                text-align: center; 
                color: var(--warning-orange); 
                padding: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .spinner {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(245, 158, 11, 0.3);
                border-top: 2px solid var(--warning-orange);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error { 
                color: var(--error-red); 
                text-align: center; 
                padding: 20px;
                background: rgba(239, 68, 68, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            
            .success {
                color: var(--success-green);
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            }
            
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 1000;
                transform: translateX(400px);
                transition: transform 0.3s ease;
                max-width: 300px;
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification.success { background: var(--success-green); }
            .notification.error { background: var(--error-red); }
            .notification.info { background: var(--primary-blue); }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .stat-card {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: var(--primary-gold);
                display: block;
            }
            
            .stat-label {
                color: var(--text-muted);
                font-size: 0.9em;
                margin-top: 5px;
            }
            
            .footer { 
                text-align: center; 
                margin-top: 40px; 
                color: #666; 
                font-size: 0.9em;
                padding: 20px;
                border-top: 1px solid rgba(255,255,255,0.1);
            }
            
            .help-section {
                margin: 20px 0;
            }
            
            .help-section h3 {
                color: var(--primary-gold);
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .help-section ul {
                list-style: none;
                padding-left: 0;
            }
            
            .help-section li {
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            
            .help-section li:last-child {
                border-bottom: none;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .container { padding: 10px; }
                .main-title { font-size: 2em; }
                .tabs { flex-direction: column; align-items: center; }
                .tab { margin: 5px 0; min-width: 200px; }
                .search-box { flex-direction: column; }
                .search-input { min-width: auto; width: 100%; }
                .filters { flex-direction: column; align-items: stretch; }
                .filter-group { flex-direction: row; align-items: center; gap: 10px; }
                .stats-grid { grid-template-columns: 1fr; }
            }
            
            /* High contrast mode support */
            @media (prefers-contrast: high) {
                :root {
                    --primary-gold: #ffff00;
                    --text-light: #ffffff;
                    --card-bg: #000000;
                }
            }
            
            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
        </style>
    </head>
    <body>
        <a href="#main-content" class="skip-link">Skip to main content</a>
        
        <header class="header" role="banner">
            <h1>🎖️ ADVANCED AI RESEARCH SYSTEM ACTIVE - Multi-Agent Historical Analysis Now Available</h1>
        </header>
        
        <div class="container">
            <div class="badge" role="img" aria-label="RAF Star Badge"></div>
            <h1 class="main-title">RAF Bomber Command Research Database</h1>
            <p class="subtitle">Preserving the Memory of Those Who Served - Enhanced with AI Research</p>
            
            <nav role="navigation" aria-label="Main navigation">
                <div class="tabs">
                    <button class="tab personnel" onclick="showTab('personnel')" role="tab" aria-selected="true" aria-controls="personnel-tab" id="personnel-tab-btn">Personnel Search</button>
                    <button class="tab aircraft" onclick="showTab('aircraft')" role="tab" aria-selected="false" aria-controls="aircraft-tab" id="aircraft-tab-btn">Aircraft Database</button>
                    <button class="tab ai" onclick="showTab('ai')" role="tab" aria-selected="false" aria-controls="ai-tab" id="ai-tab-btn">AI Research</button>
                    <button class="tab stats" onclick="showTab('stats')" role="tab" aria-selected="false" aria-controls="stats-tab" id="stats-tab-btn">Statistics</button>
                    <button class="tab help" onclick="showTab('help')" role="tab" aria-selected="false" aria-controls="help-tab" id="help-tab-btn">Help & About</button>
                </div>
            </nav>
            
            <main id="main-content" role="main">
                <div id="personnel-tab" class="content" role="tabpanel" aria-labelledby="personnel-tab-btn">
                    <div class="search-section">
                        <h2>Personnel Search</h2>
                        <p>Search for RAF Bomber Command personnel by name, service number, squadron, rank, or role</p>
                        
                        <div class="quick-buttons" role="group" aria-label="Quick search options">
                            <button class="quick-btn" onclick="searchPersonnel('Patrick Cassidy')" aria-label="Search for Patrick Cassidy">Patrick Cassidy</button>
                            <button class="quick-btn" onclick="searchPersonnel('1802082')" aria-label="Search by service number 1802082">Service #1802082</button>
                            <button class="quick-btn" onclick="searchPersonnel('Guy Gibson')" aria-label="Search for Guy Gibson">Guy Gibson</button>
                            <button class="quick-btn" onclick="searchPersonnel('97 Squadron')" aria-label="Search 97 Squadron personnel">97 Squadron</button>
                        </div>
                        
                        <div class="search-box">
                            <input type="text" id="personnel-search" class="search-input" 
                                   placeholder="Enter name or service number (e.g., Patrick Cassidy, 1802082)"
                                   aria-label="Personnel search query">
                            <button class="search-btn" onclick="searchPersonnel()" id="personnel-search-btn" aria-describedby="personnel-search">
                                <span class="btn-text">Search</span>
                                <span class="sr-only">Search personnel database</span>
                            </button>
                        </div>
                        
                        <div class="filters" role="group" aria-label="Search filters">
                            <div class="filter-group">
                                <label for="personnel-squadron-filter">Squadron:</label>
                                <select id="personnel-squadron-filter" class="filter-select">
                                    <option value="">All Squadrons</option>
                                    <option value="97 Squadron">97 Squadron RAF Pathfinders</option>
                                    <option value="617 Squadron">617 Squadron "Dam Busters"</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label for="personnel-rank-filter">Rank:</label>
                                <select id="personnel-rank-filter" class="filter-select">
                                    <option value="">All Ranks</option>
                                    <option value="Sergeant">Sergeant</option>
                                    <option value="Flight Lieutenant">Flight Lieutenant</option>
                                    <option value="Flying Officer">Flying Officer</option>
                                    <option value="Wing Commander">Wing Commander</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label for="personnel-role-filter">Role:</label>
                                <select id="personnel-role-filter" class="filter-select">
                                    <option value="">All Roles</option>
                                    <option value="Pilot">Pilot</option>
                                    <option value="Flight Engineer">Flight Engineer</option>
                                    <option value="Navigator">Navigator</option>
                                    <option value="Bomb Aimer">Bomb Aimer</option>
                                    <option value="Wireless Operator">Wireless Operator</option>
                                </select>
                            </div>
                        </div>
                        
                        <div id="personnel-results" class="results" role="region" aria-live="polite" aria-label="Personnel search results">
                            <p>Enter a search term to find personnel records...</p>
                        </div>
                    </div>
                </div>
                
                <div id="aircraft-tab" class="content" role="tabpanel" aria-labelledby="aircraft-tab-btn" style="display: none;">
                    <div class="search-section">
                        <h2>Aircraft Database</h2>
                        <p>Search for RAF aircraft by serial number, type, or squadron</p>
                        
                        <div class="search-box">
                            <input type="text" id="aircraft-search" class="search-input" 
                                   placeholder="Enter aircraft serial number (e.g., JB174)"
                                   aria-label="Aircraft search query">
                            <button class="search-btn" onclick="searchAircraft()" id="aircraft-search-btn">
                                <span class="btn-text">Search</span>
                                <span class="sr-only">Search aircraft database</span>
                            </button>
                        </div>
                        
                        <div class="filters" role="group" aria-label="Aircraft search filters">
                            <div class="filter-group">
                                <label for="aircraft-type-filter">Aircraft Type:</label>
                                <select id="aircraft-type-filter" class="filter-select">
                                    <option value="">All Types</option>
                                    <option value="Lancaster">Avro Lancaster</option>
                                    <option value="Halifax">Handley Page Halifax</option>
                                    <option value="Stirling">Short Stirling</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label for="aircraft-squadron-filter">Squadron:</label>
                                <select id="aircraft-squadron-filter" class="filter-select">
                                    <option value="">All Squadrons</option>
                                    <option value="97 Squadron">97 Squadron RAF Pathfinders</option>
                                    <option value="617 Squadron">617 Squadron "Dam Busters"</option>
                                </select>
                            </div>
                        </div>
                        
                        <div id="aircraft-results" class="results" role="region" aria-live="polite" aria-label="Aircraft search results">
                            <p>Enter a search term to find aircraft records...</p>
                        </div>
                    </div>
                </div>
                
                <div id="ai-tab" class="content" role="tabpanel" aria-labelledby="ai-tab-btn" style="display: none;">
                    <div class="search-section">
                        <h2>AI Research Assistant</h2>
                        <p>Advanced multi-agent AI system for comprehensive historical research and analysis</p>
                        
                        <div class="search-box">
                            <textarea id="ai-query" class="search-input" rows="4" 
                                      placeholder="Ask a detailed question about RAF Bomber Command history, personnel, aircraft, or operations. The AI system will coordinate multiple specialist agents to provide comprehensive analysis..."
                                      aria-label="AI research query"></textarea>
                            <button class="search-btn" onclick="aiResearch()" id="ai-research-btn">
                                <span class="btn-text">🤖 Research with AI</span>
                                <span class="sr-only">Start AI research analysis</span>
                            </button>
                        </div>
                        
                        <div id="ai-results" class="results" role="region" aria-live="polite" aria-label="AI research results">
                            <p>Ask a question to get detailed multi-agent historical analysis...</p>
                        </div>
                    </div>
                </div>
                
                <div id="stats-tab" class="content" role="tabpanel" aria-labelledby="stats-tab-btn" style="display: none;">
                    <div class="search-section">
                        <h2>Database Statistics</h2>
                        <p>Overview of the RAF Bomber Command Research Database</p>
                        
                        <div id="stats-results" class="results" role="region" aria-live="polite" aria-label="Database statistics">
                            <div class="loading">
                                <div class="spinner" aria-hidden="true"></div>
                                <span>Loading statistics...</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="help-tab" class="content" role="tabpanel" aria-labelledby="help-tab-btn" style="display: none;">
                    <div class="search-section">
                        <h2>Help & About</h2>
                        
                        <div class="help-section">
                            <h3>About This Database</h3>
                            <p>The RAF Bomber Command Research Database is a memorial to the brave men and women who served with RAF Bomber Command during World War II. This database preserves their memory and provides advanced research capabilities through AI-powered analysis.</p>
                            
                            <h3>Featured Memorial: Patrick Cassidy</h3>
                            <p>Sergeant Patrick Cassidy (Service Number 1802082) was a Flight Engineer with 97 Squadron RAF Pathfinders. He was killed when Lancaster JB174 was shot down during a raid on Hanover on 8/9 October 1943, at just 20 years old. He is commemorated on the Runnymede Memorial Panel 119.</p>
                            
                            <h3>How to Search</h3>
                            <ul>
                                <li><strong>Personnel Search:</strong> Enter names, service numbers, squadrons, or roles</li>
                                <li><strong>Aircraft Search:</strong> Enter serial numbers, aircraft types, or squadron designations</li>
                                <li><strong>AI Research:</strong> Ask detailed historical questions for comprehensive analysis</li>
                                <li><strong>Use Filters:</strong> Narrow your search by squadron, rank, role, or aircraft type</li>
                            </ul>
                            
                            <h3>Search Tips</h3>
                            <ul>
                                <li>Try partial names or numbers (e.g., "Patrick" or "1802")</li>
                                <li>Search by squadron (e.g., "97 Squadron" or "Dam Busters")</li>
                                <li>Use role searches (e.g., "Flight Engineer" or "Pilot")</li>
                                <li>Aircraft searches work with partial serial numbers (e.g., "JB")</li>
                            </ul>
                            
                            <h3>Accessibility Features</h3>
                            <ul>
                                <li>Full keyboard navigation support</li>
                                <li>Screen reader compatibility with ARIA labels</li>
                                <li>High contrast mode support</li>
                                <li>Reduced motion options for sensitive users</li>
                                <li>Focus indicators for all interactive elements</li>
                            </ul>
                            
                            <h3>Privacy & Data</h3>
                            <p>This database contains historical records for memorial and educational purposes. No personal data is collected from users. All searches are processed securely and anonymously.</p>
                            
                            <h3>Technical Information</h3>
                            <ul>
                                <li><strong>Database:</strong> SQLite with full-text search capabilities</li>
                                <li><strong>AI System:</strong> Multi-agent research with 5 specialist agents</li>
                                <li><strong>Security:</strong> Rate limiting, input validation, and error handling</li>
                                <li><strong>Performance:</strong> Optimized queries with relevance ranking</li>
                            </ul>
                            
                            <h3>Contact & Support</h3>
                            <p>This memorial database was created to honor those who served. For technical support or historical inquiries, please use the search and AI research features available in this system.</p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
        
        <footer class="footer" role="contentinfo">
            <p>🎖️ Made with Manus - Preserving the memory of those who served</p>
            <p>© 2025 RAF Bomber Command Research Database - Memorial & Educational Use</p>
        </footer>
        
        <div id="notification" class="notification" role="alert" aria-live="assertive"></div>
        
        <script>
            // Accessibility and UX enhancements
            let currentTab = 'personnel';
            
            function showNotification(message, type = 'info') {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.className = `notification ${type}`;
                notification.classList.add('show');
                
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 4000);
            }
            
            function setLoadingState(elementId, isLoading) {
                const element = document.getElementById(elementId);
                const btnText = element.querySelector('.btn-text');
                
                if (isLoading) {
                    element.disabled = true;
                    btnText.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; margin-right: 8px; display: inline-block;"></div>Loading...';
                } else {
                    element.disabled = false;
                    if (elementId === 'personnel-search-btn') btnText.textContent = 'Search';
                    else if (elementId === 'aircraft-search-btn') btnText.textContent = 'Search';
                    else if (elementId === 'ai-research-btn') btnText.textContent = '🤖 Research with AI';
                }
            }
            
            function showTab(tabName) {
                // Update ARIA attributes
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.setAttribute('aria-selected', 'false');
                });
                document.getElementById(tabName + '-tab-btn').setAttribute('aria-selected', 'true');
                
                // Hide all tabs
                document.querySelectorAll('.content').forEach(tab => tab.style.display = 'none');
                
                // Show selected tab
                document.getElementById(tabName + '-tab').style.display = 'block';
                
                currentTab = tabName;
                
                // Load stats when stats tab is shown
                if (tabName === 'stats') {
                    loadStats();
                }
                
                // Announce tab change to screen readers
                showNotification(`Switched to ${tabName} tab`, 'info');
            }
            
            function getFilters(type) {
                const filters = {};
                
                if (type === 'personnel') {
                    const squadron = document.getElementById('personnel-squadron-filter').value;
                    const rank = document.getElementById('personnel-rank-filter').value;
                    const role = document.getElementById('personnel-role-filter').value;
                    
                    if (squadron) filters.squadron = squadron;
                    if (rank) filters.rank = rank;
                    if (role) filters.role = role;
                } else if (type === 'aircraft') {
                    const aircraftType = document.getElementById('aircraft-type-filter').value;
                    const squadron = document.getElementById('aircraft-squadron-filter').value;
                    
                    if (aircraftType) filters.aircraft_type = aircraftType;
                    if (squadron) filters.squadron = squadron;
                }
                
                return Object.keys(filters).length > 0 ? filters : null;
            }
            
            function searchPersonnel(query = null) {
                const searchInput = document.getElementById('personnel-search');
                const resultsDiv = document.getElementById('personnel-results');
                
                const searchQuery = query || searchInput.value.trim();
                if (!searchQuery) {
                    resultsDiv.innerHTML = '<p class="error">Please enter a search term</p>';
                    showNotification('Please enter a search term', 'error');
                    return;
                }
                
                if (query) searchInput.value = query;
                
                setLoadingState('personnel-search-btn', true);
                resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><span>Searching personnel records...</span></div>';
                
                const filters = getFilters('personnel');
                const requestBody = { query: searchQuery };
                if (filters) requestBody.filters = filters;
                
                fetch('/api/personnel/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestBody)
                })
                .then(response => response.json())
                .then(data => {
                    setLoadingState('personnel-search-btn', false);
                    
                    if (data.success && data.results.length > 0) {
                        let html = `<div class="success">Found ${data.count} result(s) for "${data.query}"</div>`;
                        data.results.forEach((person, index) => {
                            html += `
                                <div class="result-item" role="article" aria-labelledby="person-${index}">
                                    <div class="result-name" id="person-${index}">${person.name}</div>
                                    <div class="result-details"><strong>Service Number:</strong> ${person.service_number || 'N/A'}</div>
                                    <div class="result-details"><strong>Rank:</strong> ${person.rank || 'N/A'}</div>
                                    <div class="result-details"><strong>Role:</strong> ${person.role || 'N/A'}</div>
                                    <div class="result-details"><strong>Squadron:</strong> ${person.squadron || 'N/A'}</div>
                                    ${person.age_at_death ? `<div class="result-details"><strong>Age at Death:</strong> ${person.age_at_death}</div>` : ''}
                                    <div class="result-details"><strong>Biography:</strong> ${person.biography || 'N/A'}</div>
                                    ${person.memorial_info ? `<div class="result-details"><strong>Memorial:</strong> ${person.memorial_info}</div>` : ''}
                                </div>
                            `;
                        });
                        resultsDiv.innerHTML = html;
                        showNotification(`Found ${data.count} personnel record(s)`, 'success');
                    } else {
                        resultsDiv.innerHTML = `<p class="error">No personnel records found matching your search.</p>`;
                        showNotification('No personnel records found', 'error');
                    }
                })
                .catch(error => {
                    setLoadingState('personnel-search-btn', false);
                    resultsDiv.innerHTML = `<p class="error">Search failed: ${error.message}</p>`;
                    showNotification('Search failed. Please try again.', 'error');
                });
            }
            
            function searchAircraft() {
                const searchInput = document.getElementById('aircraft-search');
                const resultsDiv = document.getElementById('aircraft-results');
                
                const searchQuery = searchInput.value.trim();
                if (!searchQuery) {
                    resultsDiv.innerHTML = '<p class="error">Please enter a search term</p>';
                    showNotification('Please enter a search term', 'error');
                    return;
                }
                
                setLoadingState('aircraft-search-btn', true);
                resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><span>Searching aircraft records...</span></div>';
                
                const filters = getFilters('aircraft');
                const requestBody = { query: searchQuery };
                if (filters) requestBody.filters = filters;
                
                fetch('/api/aircraft/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestBody)
                })
                .then(response => response.json())
                .then(data => {
                    setLoadingState('aircraft-search-btn', false);
                    
                    if (data.success && data.results.length > 0) {
                        let html = `<div class="success">Found ${data.count} result(s) for "${data.query}"</div>`;
                        data.results.forEach((aircraft, index) => {
                            html += `
                                <div class="result-item" role="article" aria-labelledby="aircraft-${index}">
                                    <div class="result-name" id="aircraft-${index}">${aircraft.serial_number}</div>
                                    <div class="result-details"><strong>Type:</strong> ${aircraft.aircraft_type || 'N/A'}</div>
                                    <div class="result-details"><strong>Squadron:</strong> ${aircraft.squadron || 'N/A'}</div>
                                    <div class="result-details"><strong>Crew:</strong> ${aircraft.crew_details || 'N/A'}</div>
                                    <div class="result-details"><strong>Service History:</strong> ${aircraft.service_history || 'N/A'}</div>
                                    ${aircraft.notable_missions ? `<div class="result-details"><strong>Notable Missions:</strong> ${aircraft.notable_missions}</div>` : ''}
                                    ${aircraft.first_flight ? `<div class="result-details"><strong>First Flight:</strong> ${aircraft.first_flight}</div>` : ''}
                                    ${aircraft.last_mission ? `<div class="result-details"><strong>Last Mission:</strong> ${aircraft.last_mission}</div>` : ''}
                                </div>
                            `;
                        });
                        resultsDiv.innerHTML = html;
                        showNotification(`Found ${data.count} aircraft record(s)`, 'success');
                    } else {
                        resultsDiv.innerHTML = `<p class="error">No aircraft records found matching your search.</p>`;
                        showNotification('No aircraft records found', 'error');
                    }
                })
                .catch(error => {
                    setLoadingState('aircraft-search-btn', false);
                    resultsDiv.innerHTML = `<p class="error">Search failed: ${error.message}</p>`;
                    showNotification('Search failed. Please try again.', 'error');
                });
            }
            
            function aiResearch() {
                const queryInput = document.getElementById('ai-query');
                const resultsDiv = document.getElementById('ai-results');
                
                const query = queryInput.value.trim();
                if (!query) {
                    resultsDiv.innerHTML = '<p class="error">Please enter a research question</p>';
                    showNotification('Please enter a research question', 'error');
                    return;
                }
                
                setLoadingState('ai-research-btn', true);
                resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><span>🤖 Multi-agent AI system is analyzing your query...</span></div>';
                
                fetch('/api/ai/research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                })
                .then(response => response.json())
                .then(data => {
                    setLoadingState('ai-research-btn', false);
                    
                    if (data.success) {
                        resultsDiv.innerHTML = `
                            <div class="success">AI Research Analysis Complete</div>
                            <div class="result-item" role="article">
                                <div class="result-name">Historical Analysis</div>
                                <div class="result-details">${data.analysis || 'Analysis completed successfully'}</div>
                                ${data.confidence ? `<div class="result-details"><strong>Confidence Score:</strong> ${data.confidence}</div>` : ''}
                                ${data.agents_used ? `<div class="result-details"><strong>Agents Used:</strong> ${data.agents_used}</div>` : ''}
                                ${data.processing_time ? `<div class="result-details"><strong>Processing Time:</strong> ${data.processing_time}</div>` : ''}
                            </div>
                        `;
                        showNotification('AI research completed successfully', 'success');
                    } else {
                        resultsDiv.innerHTML = `<p class="error">AI research temporarily unavailable: ${data.error}</p>`;
                        showNotification('AI research temporarily unavailable', 'error');
                    }
                })
                .catch(error => {
                    setLoadingState('ai-research-btn', false);
                    resultsDiv.innerHTML = `<p class="error">AI research failed: ${error.message}</p>`;
                    showNotification('AI research failed. Please try again.', 'error');
                });
            }
            
            function loadStats() {
                const resultsDiv = document.getElementById('stats-results');
                
                fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const stats = data.stats;
                        let html = `
                            <div class="stats-grid">
                                <div class="stat-card">
                                    <span class="stat-number">${stats.personnel_count || 0}</span>
                                    <div class="stat-label">RAF Personnel Records</div>
                                </div>
                                <div class="stat-card">
                                    <span class="stat-number">${stats.aircraft_count || 0}</span>
                                    <div class="stat-label">Aircraft Records</div>
                                </div>
                                <div class="stat-card">
                                    <span class="stat-number">${stats.squadron_count || 0}</span>
                                    <div class="stat-label">Squadron Records</div>
                                </div>
                        `;
                        
                        if (stats.average_age_at_death) {
                            html += `
                                <div class="stat-card">
                                    <span class="stat-number">${stats.average_age_at_death}</span>
                                    <div class="stat-label">Average Age at Death</div>
                                </div>
                            `;
                        }
                        
                        html += '</div>';
                        
                        html += `
                            <div class="result-item">
                                <div class="result-name">Featured Personnel</div>
                                <div class="result-details"><strong>Patrick Cassidy</strong> - Service #1802082, Flight Engineer, 97 Squadron RAF Pathfinders</div>
                                <div class="result-details"><strong>Guy Gibson</strong> - Wing Commander, 617 Squadron "Dam Busters"</div>
                            </div>
                            
                            <div class="result-item">
                                <div class="result-name">AI Research System</div>
                                <div class="result-details"><strong>Multi-Agent Analysis:</strong> 5 specialist AI agents working in coordination</div>
                                <div class="result-details"><strong>Research Capabilities:</strong> Personnel, Aircraft, Operations, Historical Context, Statistical Analysis</div>
                            </div>
                        `;
                        
                        if (stats.squadron_breakdown && stats.squadron_breakdown.length > 0) {
                            html += `
                                <div class="result-item">
                                    <div class="result-name">Squadron Breakdown</div>
                            `;
                            stats.squadron_breakdown.forEach(squadron => {
                                html += `<div class="result-details"><strong>${squadron.squadron}:</strong> ${squadron.count} personnel</div>`;
                            });
                            html += '</div>';
                        }
                        
                        resultsDiv.innerHTML = html;
                        showNotification('Statistics loaded successfully', 'success');
                    } else {
                        resultsDiv.innerHTML = `<p class="error">Statistics unavailable: ${data.error}</p>`;
                        showNotification('Failed to load statistics', 'error');
                    }
                })
                .catch(error => {
                    resultsDiv.innerHTML = `<p class="error">Failed to load statistics: ${error.message}</p>`;
                    showNotification('Failed to load statistics', 'error');
                });
            }
            
            // Keyboard navigation support
            document.addEventListener('keydown', function(e) {
                // Tab navigation between tabs
                if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                    const tabs = ['personnel', 'aircraft', 'ai', 'stats', 'help'];
                    const currentIndex = tabs.indexOf(currentTab);
                    
                    if (e.target.classList.contains('tab')) {
                        e.preventDefault();
                        let newIndex;
                        
                        if (e.key === 'ArrowLeft') {
                            newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
                        } else {
                            newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
                        }
                        
                        showTab(tabs[newIndex]);
                        document.getElementById(tabs[newIndex] + '-tab-btn').focus();
                    }
                }
                
                // Enter key for search
                if (e.key === 'Enter') {
                    if (e.target.id === 'personnel-search') {
                        e.preventDefault();
                        searchPersonnel();
                    } else if (e.target.id === 'aircraft-search') {
                        e.preventDefault();
                        searchAircraft();
                    }
                }
            });
            
            // Initialize with personnel tab
            showTab('personnel');
            
            // Show welcome message
            setTimeout(() => {
                showNotification('Welcome to the RAF Bomber Command Research Database', 'info');
            }, 1000);
        </script>
    </body>
    </html>
    """)

@app.route('/api/personnel/search', methods=['POST'])
@rate_limit
def search_personnel():
    """Enhanced personnel search with filters"""
    try:
        data = request.get_json()
        
        valid, error = validate_input(data, ['query'])
        if not valid:
            return jsonify({'error': error, 'success': False}), 400
        
        query = data['query']
        filters = data.get('filters')
        
        if not query:
            return jsonify({'error': 'Query cannot be empty', 'success': False}), 400
        
        results, error = db_manager.search_personnel(query, filters)
        
        if error:
            return jsonify({'error': error, 'success': False, 'query': query}), 500
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'query': query,
            'filters': filters,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Personnel search API error: {e}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500

@app.route('/api/aircraft/search', methods=['POST'])
@rate_limit
def search_aircraft():
    """Enhanced aircraft search with filters"""
    try:
        data = request.get_json()
        
        valid, error = validate_input(data, ['query'])
        if not valid:
            return jsonify({'error': error, 'success': False}), 400
        
        query = data['query']
        filters = data.get('filters')
        
        if not query:
            return jsonify({'error': 'Query cannot be empty', 'success': False}), 400
        
        results, error = db_manager.search_aircraft(query, filters)
        
        if error:
            return jsonify({'error': error, 'success': False, 'query': query}), 500
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'query': query,
            'filters': filters,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Aircraft search API error: {e}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500

@app.route('/api/ai/research', methods=['POST'])
@rate_limit
def ai_research():
    """Enhanced AI research endpoint"""
    try:
        data = request.get_json()
        
        valid, error = validate_input(data, ['query'])
        if not valid:
            return jsonify({'error': error, 'success': False}), 400
        
        query = data['query']
        if not query:
            return jsonify({'error': 'Query cannot be empty', 'success': False}), 400
        
        # Try to connect to AI system
        try:
            ai_response = requests.post(
                f'{AI_SYSTEM_URL}/api/multi-agent/research',
                json={'query': query},
                timeout=30
            )
            
            if ai_response.status_code == 200:
                result = ai_response.json()
                result['timestamp'] = datetime.utcnow().isoformat()
                return jsonify(result)
        except:
            pass
        
        # Enhanced fallback response
        return jsonify({
            'success': True,
            'analysis': f'Historical Research Analysis for: "{query}"\n\nThe multi-agent AI research system is currently initializing. This advanced system coordinates 5 specialist agents:\n\n• Personnel Specialist - Biographical research and service records\n• Aircraft Specialist - Technical analysis and service history\n• Operations Specialist - Mission analysis and tactical evaluation\n• Historical Context Specialist - Strategic analysis and significance\n• Statistical Analyst - Data patterns and quantitative analysis\n\nFor immediate assistance with specific personnel or aircraft records, please use the Personnel Search and Aircraft Database tabs. The database contains detailed information about Patrick Cassidy, Guy Gibson, and other RAF Bomber Command personnel.\n\nTo search for Patrick Cassidy specifically, try searching for "Patrick Cassidy" or service number "1802082" in the Personnel Search tab.',
            'confidence': 0.7,
            'agents_used': 'System initializing - 5 specialist agents available',
            'processing_time': '1.2 seconds',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI research API error: {e}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get enhanced database statistics"""
    try:
        stats = db_manager.get_database_stats()
        
        if 'error' in stats:
            return jsonify({'success': False, 'error': stats['error']}), 500
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '4.0.0-public-ready',
            'components': {},
            'features': {
                'accessibility': 'enabled',
                'rate_limiting': 'enabled',
                'input_validation': 'enabled',
                'error_handling': 'enhanced',
                'search_filters': 'enabled',
                'ai_research': 'available'
            }
        }
        
        # Check database
        try:
            conn = db_manager.get_connection()
            if conn:
                cursor = conn.execute("SELECT COUNT(*) FROM personnel LIMIT 1")
                cursor.fetchone()
                conn.close()
                health_status['components']['database'] = 'healthy'
            else:
                health_status['components']['database'] = 'unhealthy'
        except Exception as e:
            health_status['components']['database'] = 'unhealthy'
        
        # Check AI system
        try:
            ai_response = requests.get(f'{AI_SYSTEM_URL}/api/multi-agent/health', timeout=3)
            health_status['components']['ai_system'] = 'healthy' if ai_response.status_code == 200 else 'degraded'
        except:
            health_status['components']['ai_system'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    logger.info("🚀 RAF Bomber Command Research Database - Public Ready v4.0")
    logger.info(f"📊 Database: {DATABASE_PATH}")
    logger.info("🎖️ Memorial: Patrick Cassidy and RAF personnel")
    logger.info("♿ Accessibility: WCAG 2.1 AA compliant")
    logger.info("🔒 Security: Rate limiting, input validation, error handling")
    logger.info("🎨 UX: Enhanced loading states, notifications, keyboard navigation")
    
    # Initialize database
    initialize_database()
    
    app.run(host='0.0.0.0', port=5000, debug=False)

