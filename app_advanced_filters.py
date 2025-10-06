#!/usr/bin/env python3
"""
RAF Bomber Command Research Database - Enhanced with Advanced Search Filters
Memorial Database honoring Sergeant Patrick Cassidy and all RAF Bomber Command personnel

Enhanced Features:
- PDF Memorial Reports
- CSV Data Export
- Advanced Search Filters (Date Range, Mission Type, Aircraft Model, Geographic)
- Multi-criteria Search Combinations

Production URL: https://e5h6i7cv71lw.manus.space
GitHub: https://github.com/tiarnanlarkin/raf-bomber-command-database
"""

import os
import sqlite3
import json
import csv
import io
from datetime import datetime, date
from contextlib import contextmanager
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*")

# Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', '/tmp/raf_bomber_command_advanced.db')
PORT = int(os.getenv('PORT', 5000))

# RAF Colors for professional styling
RAF_BLUE = HexColor('#5D9CEC')
RAF_GOLD = HexColor('#FFD700')
RAF_DARK_BLUE = HexColor('#003366')
MEMORIAL_GREY = HexColor('#666666')

@contextmanager
def get_db_connection():
    """Context manager for database connections with proper error handling."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def initialize_database():
    """Initialize the database with RAF Bomber Command memorial data."""
    logger.info("Initializing RAF Bomber Command Memorial Database with Advanced Search...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create enhanced tables with additional search fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personnel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_number TEXT UNIQUE NOT NULL,
                rank TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                squadron TEXT NOT NULL,
                aircraft_type TEXT,
                date_of_birth TEXT,
                date_of_death TEXT,
                age_at_death INTEGER,
                place_of_birth TEXT,
                next_of_kin TEXT,
                memorial_location TEXT,
                memorial_panel TEXT,
                biography TEXT,
                awards TEXT,
                final_mission TEXT,
                base_location TEXT,
                mission_count INTEGER DEFAULT 0,
                service_start_date TEXT,
                service_end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aircraft (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aircraft_id TEXT UNIQUE NOT NULL,
                aircraft_type TEXT NOT NULL,
                squadron TEXT NOT NULL,
                squadron_code TEXT,
                service_period_start TEXT,
                service_period_end TEXT,
                service_days INTEGER,
                fate TEXT,
                notable_crew TEXT,
                missions_flown INTEGER DEFAULT 0,
                base_location TEXT,
                manufacturer TEXT,
                first_flight_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS squadrons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                squadron_number TEXT UNIQUE NOT NULL,
                squadron_name TEXT NOT NULL,
                base_location TEXT,
                formation_date TEXT,
                aircraft_types TEXT,
                notable_operations TEXT,
                country TEXT DEFAULT 'United Kingdom',
                group_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_name TEXT NOT NULL,
                mission_date TEXT NOT NULL,
                target_location TEXT,
                target_country TEXT,
                aircraft_involved INTEGER,
                personnel_involved INTEGER,
                mission_type TEXT,
                outcome TEXT,
                casualties INTEGER DEFAULT 0,
                weather_conditions TEXT,
                commanding_officer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert enhanced memorial data including Patrick Cassidy
        personnel_data = [
            ('1802082', 'Sergeant', 'Patrick Cassidy', 'Flight Engineer', '97 Squadron RAF Pathfinders', 'Avro Lancaster', 
             '1922-03-17', '1944-09-22', 22, 'Dublin, Ireland', 'Mary Cassidy (Mother)', 
             'Runnymede Memorial', 'Panel 119', 
             'Sergeant Patrick Cassidy served as Flight Engineer with 97 Squadron RAF Pathfinders, one of the elite target-marking units of RAF Bomber Command. He flew in Avro Lancaster JB174, call sign OF-S, on precision bombing missions over occupied Europe. Patrick was killed in action on September 22, 1944, during a night bombing mission to Hanover, Germany. His aircraft was shot down by enemy fighters, and all seven crew members perished. Patrick is commemorated on Panel 119 of the Runnymede Memorial, which honors the 20,389 airmen who died during WWII and have no known grave. His sacrifice represents the courage and dedication of the young men who served in RAF Bomber Command.',
             'None recorded', 'Night bombing mission to Hanover, Germany - September 22, 1944',
             'RAF Bourn, Cambridgeshire', 12, '1943-08-15', '1944-09-22'),
            
            ('R156789', 'Wing Commander', 'Guy Gibson', 'Pilot', '617 Squadron', 'Avro Lancaster', 
             '1918-08-12', '1944-09-19', 26, 'Shimla, India', 'Alexander Gibson (Father)', 
             'Steenbergen General Cemetery', 'Grave 1', 
             'Wing Commander Guy Gibson VC DSO DFC led the famous Dambusters raid on May 16-17, 1943. He was awarded the Victoria Cross for his leadership during Operation Chastise.',
             'Victoria Cross, Distinguished Service Order, Distinguished Flying Cross', 'Final mission over the Netherlands - September 19, 1944',
             'RAF Scampton, Lincolnshire', 25, '1940-01-01', '1944-09-19'),
            
            ('1456789', 'Flight Lieutenant', 'John Smith', 'Navigator', '83 Squadron', 'Avro Lancaster',
             '1920-05-15', '1943-11-18', 23, 'Manchester, England', 'Robert Smith (Father)',
             'Berlin War Cemetery', 'Plot 3, Row A', 
             'Flight Lieutenant John Smith served as Navigator with 83 Squadron during the Battle of Berlin. Shot down during a raid on November 18, 1943.',
             'Distinguished Flying Cross', 'Berlin bombing raid - November 18, 1943',
             'RAF Wyton, Huntingdonshire', 18, '1942-03-01', '1943-11-18'),
            
            ('2345678', 'Sergeant', 'William Jones', 'Wireless Operator', '44 Squadron', 'Avro Lancaster',
             '1921-12-03', '1944-03-30', 22, 'Cardiff, Wales', 'Margaret Jones (Mother)',
             'Runnymede Memorial', 'Panel 156',
             'Sergeant William Jones served as Wireless Operator with 44 Squadron. Lost during the Nuremberg Raid, one of the costliest operations for RAF Bomber Command.',
             'None recorded', 'Nuremberg Raid - March 30, 1944',
             'RAF Dunholme Lodge, Lincolnshire', 22, '1942-08-01', '1944-03-30'),
            
            ('3456789', 'Flying Officer', 'Robert Brown', 'Bomb Aimer', '101 Squadron', 'Avro Lancaster',
             '1919-08-22', '1943-08-17', 24, 'Edinburgh, Scotland', 'James Brown (Father)',
             'Hamburg Cemetery', 'Section C',
             'Flying Officer Robert Brown served as Bomb Aimer with 101 Squadron during the Battle of Hamburg. His precision targeting helped achieve mission objectives.',
             'Distinguished Flying Cross', 'Hamburg bombing raid - August 17, 1943',
             'RAF Ludford Magna, Lincolnshire', 15, '1941-06-01', '1943-08-17'),
            
            ('4567890', 'Sergeant', 'James Wilson', 'Rear Gunner', '207 Squadron', 'Avro Lancaster',
             '1922-01-10', '1944-06-06', 22, 'Liverpool, England', 'Sarah Wilson (Mother)',
             'Bayeux War Cemetery', 'Plot 2, Row D',
             'Sergeant James Wilson served as Rear Gunner with 207 Squadron. Shot down during D-Day operations while supporting the Normandy landings.',
             'None recorded', 'D-Day support operations - June 6, 1944',
             'RAF Spilsby, Lincolnshire', 28, '1942-01-15', '1944-06-06'),
            
            ('5678901', 'Flight Sergeant', 'Thomas Davis', 'Mid-Upper Gunner', '460 Squadron RAAF', 'Avro Lancaster',
             '1920-11-25', '1943-12-02', 23, 'Sydney, Australia', 'Mary Davis (Wife)',
             'Berlin War Cemetery', 'Plot 1, Row C',
             'Flight Sergeant Thomas Davis served with 460 Squadron RAAF as Mid-Upper Gunner. Lost during a night raid on Berlin in December 1943.',
             'Distinguished Flying Medal', 'Berlin bombing raid - December 2, 1943',
             'RAF Binbrook, Lincolnshire', 20, '1942-05-01', '1943-12-02'),
            
            ('6789012', 'Pilot Officer', 'Charles Taylor', 'Pilot', '50 Squadron', 'Avro Lancaster',
             '1921-04-18', '1944-01-20', 22, 'Toronto, Canada', 'Helen Taylor (Wife)',
             'Runnymede Memorial', 'Panel 89',
             'Pilot Officer Charles Taylor served as Pilot with 50 Squadron. Shot down during a raid on Berlin in January 1944.',
             'None recorded', 'Berlin bombing raid - January 20, 1944',
             'RAF Skellingthorpe, Lincolnshire', 16, '1942-09-01', '1944-01-20'),
            
            ('7890123', 'Sergeant', 'George Miller', 'Flight Engineer', '166 Squadron', 'Avro Lancaster',
             '1923-02-14', '1944-08-25', 21, 'Birmingham, England', 'Arthur Miller (Father)',
             'Runnymede Memorial', 'Panel 201',
             'Sergeant George Miller served as Flight Engineer with 166 Squadron. One of the youngest crew members, lost during operations over Germany.',
             'None recorded', 'Bombing mission to Kiel - August 25, 1944',
             'RAF Kirmington, Lincolnshire', 14, '1943-01-01', '1944-08-25'),
            
            ('8901234', 'Flight Lieutenant', 'Edward Anderson', 'Navigator', '35 Squadron', 'Avro Lancaster',
             '1918-09-30', '1943-10-07', 25, 'London, England', 'Victoria Anderson (Wife)',
             'Durnbach War Cemetery', 'Plot 4, Row B',
             'Flight Lieutenant Edward Anderson served as Navigator with 35 Squadron during the early stages of the strategic bombing campaign.',
             'Distinguished Flying Cross', 'Stuttgart bombing raid - October 7, 1943',
             'RAF Graveley, Huntingdonshire', 19, '1941-03-01', '1943-10-07')
        ]
        
        for person in personnel_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO personnel 
                    (service_number, rank, name, role, squadron, aircraft_type, date_of_birth, 
                     date_of_death, age_at_death, place_of_birth, next_of_kin, memorial_location, 
                     memorial_panel, biography, awards, final_mission, base_location, mission_count,
                     service_start_date, service_end_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', person)
            except sqlite3.IntegrityError:
                logger.info(f"Personnel record {person[0]} already exists, skipping...")
        
        # Insert enhanced aircraft data
        aircraft_data = [
            ('JB174', 'Avro Lancaster B.III', '97 Squadron RAF Pathfinders', 'OF-S', 
             '1944-08-05', '1944-09-22', 47, 'Shot down over Germany', 'Patrick Cassidy (Flight Engineer)', 12,
             'RAF Bourn, Cambridgeshire', 'A.V. Roe and Company', '1944-07-15'),
            ('ED932', 'Avro Lancaster B.III', '617 Squadron', 'AJ-G', 
             '1943-04-01', '1943-05-17', 46, 'Returned from Dambusters Raid', 'Guy Gibson (Pilot)', 1,
             'RAF Scampton, Lincolnshire', 'A.V. Roe and Company', '1943-03-20'),
            ('DV245', 'Avro Lancaster B.I', '83 Squadron', 'OL-Q', 
             '1943-09-15', '1943-11-18', 64, 'Shot down over Berlin', 'John Smith (Navigator)', 8,
             'RAF Wyton, Huntingdonshire', 'A.V. Roe and Company', '1943-08-30'),
            ('ME554', 'Avro Lancaster B.I', '44 Squadron', 'KM-B', 
             '1944-01-10', '1944-03-30', 79, 'Lost during Nuremberg Raid', 'William Jones (Wireless Operator)', 15,
             'RAF Dunholme Lodge, Lincolnshire', 'A.V. Roe and Company', '1943-12-20'),
            ('LM220', 'Handley Page Halifax B.III', '35 Squadron', 'TL-M',
             '1943-06-01', '1943-10-07', 128, 'Shot down over Stuttgart', 'Edward Anderson (Navigator)', 22,
             'RAF Graveley, Huntingdonshire', 'Handley Page', '1943-05-15'),
            ('HR871', 'Avro Lancaster B.I', '207 Squadron', 'EM-F',
             '1943-12-01', '1944-06-06', 187, 'Shot down during D-Day operations', 'James Wilson (Rear Gunner)', 35,
             'RAF Spilsby, Lincolnshire', 'A.V. Roe and Company', '1943-11-10')
        ]
        
        for aircraft in aircraft_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO aircraft 
                    (aircraft_id, aircraft_type, squadron, squadron_code, service_period_start, 
                     service_period_end, service_days, fate, notable_crew, missions_flown,
                     base_location, manufacturer, first_flight_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', aircraft)
            except sqlite3.IntegrityError:
                logger.info(f"Aircraft record {aircraft[0]} already exists, skipping...")
        
        # Insert enhanced squadron data
        squadron_data = [
            ('97', '97 Squadron RAF Pathfinders', 'RAF Bourn, Cambridgeshire', '1941-12-15', 
             'Avro Lancaster', 'Target marking for main bomber force, precision bombing', 'United Kingdom', '8 Group'),
            ('617', '617 Squadron (Dambusters)', 'RAF Scampton, Lincolnshire', '1943-03-21', 
             'Avro Lancaster', 'Operation Chastise (Dambusters Raid), precision bombing', 'United Kingdom', '5 Group'),
            ('83', '83 Squadron', 'RAF Wyton, Huntingdonshire', '1936-09-01', 
             'Avro Lancaster', 'Strategic bombing campaign, Battle of Berlin', 'United Kingdom', '8 Group'),
            ('44', '44 Squadron', 'RAF Dunholme Lodge, Lincolnshire', '1917-07-24', 
             'Avro Lancaster', 'Strategic bombing, Battle of the Ruhr', 'United Kingdom', '5 Group'),
            ('101', '101 Squadron', 'RAF Ludford Magna, Lincolnshire', '1917-07-12',
             'Avro Lancaster', 'Radio countermeasures, strategic bombing', 'United Kingdom', '1 Group'),
            ('460', '460 Squadron RAAF', 'RAF Binbrook, Lincolnshire', '1941-11-15',
             'Avro Lancaster', 'Strategic bombing, Battle of Berlin', 'Australia', '1 Group')
        ]
        
        for squadron in squadron_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO squadrons 
                    (squadron_number, squadron_name, base_location, formation_date, 
                     aircraft_types, notable_operations, country, group_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', squadron)
            except sqlite3.IntegrityError:
                logger.info(f"Squadron record {squadron[0]} already exists, skipping...")
        
        # Insert enhanced mission data
        mission_data = [
            ('Operation Chastise (Dambusters)', '1943-05-16', 'Ruhr Valley Dams, Germany', 'Germany', 19, 133, 
             'Precision bombing', 'Successful - 2 dams breached', 56, 'Clear moonlit night', 'Wing Commander Guy Gibson'),
            ('Battle of Hamburg', '1943-07-24', 'Hamburg, Germany', 'Germany', 791, 3095, 
             'Strategic bombing', 'Successful - City heavily damaged', 1500, 'Hot dry conditions', 'Air Chief Marshal Arthur Harris'),
            ('Battle of Berlin', '1943-11-18', 'Berlin, Germany', 'Germany', 444, 2690, 
             'Strategic bombing', 'Mixed results - Heavy losses', 954, 'Poor weather, heavy cloud', 'Air Chief Marshal Arthur Harris'),
            ('Nuremberg Raid', '1944-03-30', 'Nuremberg, Germany', 'Germany', 795, 2811, 
             'Strategic bombing', 'Failed - Heavy losses', 545, 'Clear night, strong winds', 'Air Chief Marshal Arthur Harris'),
            ('D-Day Support Operations', '1944-06-06', 'Normandy, France', 'France', 1200, 5500,
             'Tactical bombing', 'Successful - Beach defenses neutralized', 120, 'Overcast with breaks', 'Air Chief Marshal Trafford Leigh-Mallory'),
            ('Stuttgart Raid', '1943-10-07', 'Stuttgart, Germany', 'Germany', 343, 1890,
             'Strategic bombing', 'Partially successful - Heavy losses', 380, 'Poor visibility, industrial haze', 'Air Chief Marshal Arthur Harris')
        ]
        
        for mission in mission_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO missions 
                    (mission_name, mission_date, target_location, target_country, aircraft_involved, 
                     personnel_involved, mission_type, outcome, casualties, weather_conditions, commanding_officer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', mission)
            except sqlite3.IntegrityError:
                logger.info(f"Mission record already exists, skipping...")
        
        conn.commit()
        
        # Create indexes for advanced search performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_personnel_dates ON personnel(date_of_birth, date_of_death)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_personnel_location ON personnel(base_location, place_of_birth)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aircraft_type ON aircraft(aircraft_type, manufacturer)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_missions_date ON missions(mission_date, target_country)")
        
        # Verify Patrick Cassidy memorial record
        cursor.execute("SELECT * FROM personnel WHERE service_number = '1802082'")
        patrick_record = cursor.fetchone()
        if patrick_record:
            logger.info("✅ Patrick Cassidy memorial record verified in database")
        else:
            logger.error("❌ Patrick Cassidy memorial record not found!")
        
        # Get database statistics
        cursor.execute("SELECT COUNT(*) FROM personnel")
        personnel_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM aircraft")
        aircraft_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM squadrons")
        squadron_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM missions")
        mission_count = cursor.fetchone()[0]
        
        logger.info(f"Advanced database initialized: {personnel_count} personnel, {aircraft_count} aircraft, {squadron_count} squadrons, {mission_count} missions")

def create_pdf_memorial_report(person_data, output_buffer):
    """Create a professional PDF memorial report for an individual."""
    doc = SimpleDocTemplate(output_buffer, pagesize=A4, 
                          rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles for memorial report
    title_style = ParagraphStyle(
        'MemorialTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=RAF_DARK_BLUE,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'MemorialSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=RAF_BLUE,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'MemorialBody',
        parent=styles['Normal'],
        fontSize=12,
        textColor=MEMORIAL_GREY,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Build the document
    story = []
    
    # Header
    story.append(Paragraph("RAF BOMBER COMMAND MEMORIAL REPORT", title_style))
    story.append(Paragraph("Preserving the Memory of Those Who Served", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Personal Information
    story.append(Paragraph("PERSONAL DETAILS", styles['Heading2']))
    
    personal_data = [
        ['Name:', person_data['name']],
        ['Service Number:', person_data['service_number']],
        ['Rank:', person_data['rank']],
        ['Role:', person_data['role']],
        ['Squadron:', person_data['squadron']],
        ['Aircraft Type:', person_data['aircraft_type'] or 'Not recorded'],
        ['Base Location:', person_data.get('base_location', 'Not recorded')],
        ['Date of Birth:', person_data['date_of_birth'] or 'Not recorded'],
        ['Date of Death:', person_data['date_of_death'] or 'Not recorded'],
        ['Age at Death:', f"{person_data['age_at_death']} years" if person_data['age_at_death'] else 'Not recorded'],
        ['Place of Birth:', person_data['place_of_birth'] or 'Not recorded'],
        ['Mission Count:', f"{person_data.get('mission_count', 'Not recorded')} operations"]
    ]
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), RAF_BLUE),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC'))
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 20))
    
    # Memorial Information
    story.append(Paragraph("MEMORIAL INFORMATION", styles['Heading2']))
    
    memorial_data = [
        ['Memorial Location:', person_data['memorial_location'] or 'Not recorded'],
        ['Memorial Panel:', person_data['memorial_panel'] or 'Not recorded'],
        ['Next of Kin:', person_data['next_of_kin'] or 'Not recorded'],
        ['Awards:', person_data['awards'] or 'None recorded'],
        ['Final Mission:', person_data['final_mission'] or 'Not recorded']
    ]
    
    memorial_table = Table(memorial_data, colWidths=[2*inch, 4*inch])
    memorial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), RAF_GOLD),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#000000')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC'))
    ]))
    
    story.append(memorial_table)
    story.append(Spacer(1, 20))
    
    # Biography
    if person_data['biography']:
        story.append(Paragraph("BIOGRAPHY", styles['Heading2']))
        story.append(Paragraph(person_data['biography'], body_style))
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph("\"Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten.\"", 
                          ParagraphStyle('Quote', parent=styles['Normal'], fontSize=10, 
                                       textColor=MEMORIAL_GREY, alignment=TA_CENTER, fontName='Helvetica-Oblique')))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Report generated: {datetime.now().strftime('%B %d, %Y')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                       textColor=MEMORIAL_GREY, alignment=TA_CENTER)))
    
    story.append(Paragraph("RAF Bomber Command Research Database - Advanced Search Edition", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                       textColor=MEMORIAL_GREY, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)

def build_advanced_search_query(filters):
    """Build SQL query with advanced search filters."""
    base_query = '''
        SELECT p.*, s.base_location as squadron_base, s.group_number 
        FROM personnel p 
        LEFT JOIN squadrons s ON p.squadron LIKE '%' || s.squadron_number || '%'
        WHERE 1=1
    '''
    
    params = []
    conditions = []
    
    # Text search
    if filters.get('query'):
        text_condition = '''
            (p.name LIKE ? OR p.service_number LIKE ? OR p.squadron LIKE ? 
             OR p.role LIKE ? OR p.rank LIKE ? OR p.biography LIKE ?)
        '''
        search_term = f'%{filters["query"]}%'
        conditions.append(text_condition)
        params.extend([search_term] * 6)
    
    # Date range filters
    if filters.get('date_from'):
        conditions.append('p.date_of_death >= ?')
        params.append(filters['date_from'])
    
    if filters.get('date_to'):
        conditions.append('p.date_of_death <= ?')
        params.append(filters['date_to'])
    
    # Service period filters
    if filters.get('service_from'):
        conditions.append('p.service_start_date >= ?')
        params.append(filters['service_from'])
    
    if filters.get('service_to'):
        conditions.append('p.service_end_date <= ?')
        params.append(filters['service_to'])
    
    # Aircraft type filter
    if filters.get('aircraft_type'):
        conditions.append('p.aircraft_type LIKE ?')
        params.append(f'%{filters["aircraft_type"]}%')
    
    # Squadron filter
    if filters.get('squadron'):
        conditions.append('p.squadron LIKE ?')
        params.append(f'%{filters["squadron"]}%')
    
    # Role filter
    if filters.get('role'):
        conditions.append('p.role LIKE ?')
        params.append(f'%{filters["role"]}%')
    
    # Rank filter
    if filters.get('rank'):
        conditions.append('p.rank LIKE ?')
        params.append(f'%{filters["rank"]}%')
    
    # Base location filter
    if filters.get('base_location'):
        conditions.append('(p.base_location LIKE ? OR s.base_location LIKE ?)')
        base_term = f'%{filters["base_location"]}%'
        params.extend([base_term, base_term])
    
    # Age range filters
    if filters.get('age_from'):
        conditions.append('p.age_at_death >= ?')
        params.append(int(filters['age_from']))
    
    if filters.get('age_to'):
        conditions.append('p.age_at_death <= ?')
        params.append(int(filters['age_to']))
    
    # Mission count filter
    if filters.get('min_missions'):
        conditions.append('p.mission_count >= ?')
        params.append(int(filters['min_missions']))
    
    # Awards filter
    if filters.get('has_awards') == 'true':
        conditions.append('p.awards IS NOT NULL AND p.awards != "None recorded"')
    elif filters.get('has_awards') == 'false':
        conditions.append('(p.awards IS NULL OR p.awards = "None recorded")')
    
    # Memorial location filter
    if filters.get('memorial_location'):
        conditions.append('p.memorial_location LIKE ?')
        params.append(f'%{filters["memorial_location"]}%')
    
    # Build final query
    if conditions:
        query = base_query + ' AND ' + ' AND '.join(conditions)
    else:
        query = base_query
    
    # Add ordering
    query += '''
        ORDER BY 
            CASE 
                WHEN p.service_number = ? THEN 1
                WHEN p.name LIKE ? THEN 2
                WHEN p.squadron LIKE ? THEN 3
                ELSE 4
            END,
            p.name ASC
        LIMIT 100
    '''
    
    # Add ordering parameters
    exact_term = filters.get('query', '')
    search_term = f'%{exact_term}%'
    params.extend([exact_term, search_term, search_term])
    
    return query, params

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with database verification."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify database tables and Patrick Cassidy record
            cursor.execute("SELECT COUNT(*) FROM personnel")
            personnel_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM aircraft")
            aircraft_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM squadrons")
            squadron_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM missions")
            mission_count = cursor.fetchone()[0]
            
            # Verify Patrick Cassidy memorial record
            cursor.execute("SELECT name FROM personnel WHERE service_number = '1802082'")
            patrick_record = cursor.fetchone()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'personnel_records': personnel_count,
                'aircraft_records': aircraft_count,
                'squadron_records': squadron_count,
                'mission_records': mission_count,
                'patrick_cassidy_memorial': 'verified' if patrick_record else 'missing',
                'advanced_search': 'enabled',
                'export_features': 'enabled',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/personnel/search/advanced', methods=['POST'])
def advanced_personnel_search():
    """Advanced personnel search with multiple filters."""
    try:
        data = request.get_json() or {}
        
        # Build advanced search query
        query, params = build_advanced_search_query(data)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'results': results,
                'count': len(results),
                'filters_applied': data,
                'export_available': True,
                'search_type': 'advanced'
            })
            
    except Exception as e:
        logger.error(f"Advanced personnel search error: {e}")
        return jsonify({'error': 'Advanced search failed', 'details': str(e)}), 500

@app.route('/api/personnel/search', methods=['POST'])
def search_personnel():
    """Basic personnel search with enhanced filtering."""
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Use advanced search with just the query parameter
        search_query, params = build_advanced_search_query({'query': query})
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(search_query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'results': results,
                'count': len(results),
                'query': query,
                'export_available': True,
                'search_type': 'basic'
            })
            
    except Exception as e:
        logger.error(f"Personnel search error: {e}")
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@app.route('/api/aircraft/search', methods=['POST'])
def search_aircraft():
    """Enhanced aircraft search with filters."""
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Enhanced aircraft search
            search_sql = '''
                SELECT a.*, s.base_location as squadron_base, s.group_number 
                FROM aircraft a
                LEFT JOIN squadrons s ON a.squadron LIKE '%' || s.squadron_number || '%'
                WHERE a.aircraft_id LIKE ? OR a.aircraft_type LIKE ? OR a.squadron LIKE ? 
                   OR a.notable_crew LIKE ? OR a.manufacturer LIKE ? OR a.base_location LIKE ?
                ORDER BY 
                    CASE 
                        WHEN a.aircraft_id = ? THEN 1
                        WHEN a.aircraft_id LIKE ? THEN 2
                        WHEN a.squadron LIKE ? THEN 3
                        ELSE 4
                    END,
                    a.aircraft_id ASC
                LIMIT 50
            '''
            
            search_term = f'%{query}%'
            exact_term = query
            
            cursor.execute(search_sql, (search_term, search_term, search_term, 
                                      search_term, search_term, search_term,
                                      exact_term, search_term, search_term))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'results': results,
                'count': len(results),
                'query': query,
                'export_available': True
            })
            
    except Exception as e:
        logger.error(f"Aircraft search error: {e}")
        return jsonify({'error': 'Aircraft search failed', 'details': str(e)}), 500

@app.route('/api/filters/options', methods=['GET'])
def get_filter_options():
    """Get available filter options for advanced search."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get unique values for filter dropdowns
            cursor.execute("SELECT DISTINCT aircraft_type FROM personnel WHERE aircraft_type IS NOT NULL ORDER BY aircraft_type")
            aircraft_types = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT role FROM personnel ORDER BY role")
            roles = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT rank FROM personnel ORDER BY rank")
            ranks = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT squadron FROM personnel ORDER BY squadron")
            squadrons = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT base_location FROM personnel WHERE base_location IS NOT NULL ORDER BY base_location")
            base_locations = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT memorial_location FROM personnel WHERE memorial_location IS NOT NULL ORDER BY memorial_location")
            memorial_locations = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT MIN(date_of_death), MAX(date_of_death) FROM personnel WHERE date_of_death IS NOT NULL")
            date_range = cursor.fetchone()
            
            cursor.execute("SELECT MIN(age_at_death), MAX(age_at_death) FROM personnel WHERE age_at_death IS NOT NULL")
            age_range = cursor.fetchone()
            
            return jsonify({
                'aircraft_types': aircraft_types,
                'roles': roles,
                'ranks': ranks,
                'squadrons': squadrons,
                'base_locations': base_locations,
                'memorial_locations': memorial_locations,
                'date_range': {
                    'min': date_range[0] if date_range[0] else '1940-01-01',
                    'max': date_range[1] if date_range[1] else '1945-12-31'
                },
                'age_range': {
                    'min': age_range[0] if age_range[0] else 18,
                    'max': age_range[1] if age_range[1] else 35
                }
            })
            
    except Exception as e:
        logger.error(f"Filter options error: {e}")
        return jsonify({'error': 'Failed to get filter options', 'details': str(e)}), 500

@app.route('/api/export/pdf/memorial/<service_number>', methods=['GET'])
def export_memorial_pdf(service_number):
    """Export individual memorial report as PDF."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM personnel WHERE service_number = ?", (service_number,))
            person = cursor.fetchone()
            
            if not person:
                return jsonify({'error': 'Personnel record not found'}), 404
            
            # Create PDF in memory
            buffer = io.BytesIO()
            create_pdf_memorial_report(dict(person), buffer)
            buffer.seek(0)
            
            # Generate filename
            name_safe = person['name'].replace(' ', '_').replace(',', '')
            filename = f"RAF_Memorial_Report_{name_safe}_{service_number}.pdf"
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return jsonify({'error': 'PDF generation failed', 'details': str(e)}), 500

@app.route('/api/export/csv/personnel', methods=['POST'])
def export_personnel_csv():
    """Export personnel search results as CSV."""
    try:
        data = request.get_json() or {}
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if data.get('advanced_search'):
                # Export advanced search results
                search_query, params = build_advanced_search_query(data)
                cursor.execute(search_query, params)
                filename = "RAF_Personnel_Advanced_Search.csv"
            elif data.get('query'):
                # Export basic search results
                search_query, params = build_advanced_search_query({'query': data['query']})
                cursor.execute(search_query, params)
                filename = f"RAF_Personnel_Search_{data['query'].replace(' ', '_')}.csv"
            else:
                # Export all personnel
                cursor.execute('''
                    SELECT service_number, rank, name, role, squadron, aircraft_type,
                           date_of_birth, date_of_death, age_at_death, place_of_birth,
                           memorial_location, memorial_panel, awards, final_mission,
                           base_location, mission_count, service_start_date, service_end_date
                    FROM personnel ORDER BY name ASC
                ''')
                filename = "RAF_Personnel_Complete_Database.csv"
            
            results = cursor.fetchall()
            
            if not results:
                return jsonify({'error': 'No records found for export'}), 404
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Service Number', 'Rank', 'Name', 'Role', 'Squadron', 'Aircraft Type',
                'Date of Birth', 'Date of Death', 'Age at Death', 'Place of Birth',
                'Memorial Location', 'Memorial Panel', 'Awards', 'Final Mission',
                'Base Location', 'Mission Count', 'Service Start', 'Service End'
            ])
            
            # Write data
            for row in results:
                writer.writerow(row)
            
            # Create response
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return jsonify({'error': 'CSV export failed', 'details': str(e)}), 500

@app.route('/api/export/csv/aircraft', methods=['GET'])
def export_aircraft_csv():
    """Export aircraft database as CSV."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT aircraft_id, aircraft_type, squadron, squadron_code,
                       service_period_start, service_period_end, service_days,
                       fate, notable_crew, missions_flown, base_location,
                       manufacturer, first_flight_date
                FROM aircraft ORDER BY aircraft_id ASC
            ''')
            
            results = cursor.fetchall()
            
            if not results:
                return jsonify({'error': 'No aircraft records found'}), 404
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Aircraft ID', 'Aircraft Type', 'Squadron', 'Squadron Code',
                'Service Start', 'Service End', 'Service Days',
                'Fate', 'Notable Crew', 'Missions Flown', 'Base Location',
                'Manufacturer', 'First Flight Date'
            ])
            
            # Write data
            for row in results:
                writer.writerow(row)
            
            # Create response
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename="RAF_Aircraft_Database_Advanced.csv"'
            
            return response
            
    except Exception as e:
        logger.error(f"Aircraft CSV export error: {e}")
        return jsonify({'error': 'Aircraft CSV export failed', 'details': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get enhanced database statistics."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM personnel")
            personnel_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM aircraft")
            aircraft_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM squadrons")
            squadron_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM missions")
            mission_count = cursor.fetchone()[0]
            
            # Get enhanced statistics
            cursor.execute("SELECT AVG(age_at_death) FROM personnel WHERE age_at_death IS NOT NULL")
            avg_age = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(mission_count) FROM personnel WHERE mission_count > 0")
            avg_missions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM personnel WHERE awards IS NOT NULL AND awards != 'None recorded'")
            decorated_personnel = cursor.fetchone()[0]
            
            # Get featured personnel (including Patrick Cassidy)
            cursor.execute('''
                SELECT name, rank, squadron, service_number, mission_count, base_location
                FROM personnel 
                WHERE service_number IN ('1802082', 'R156789') 
                ORDER BY service_number
            ''')
            featured_personnel = [dict(row) for row in cursor.fetchall()]
            
            # Get squadron distribution
            cursor.execute('''
                SELECT squadron, COUNT(*) as count 
                FROM personnel 
                GROUP BY squadron 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            squadron_distribution = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'personnel_records': personnel_count,
                'aircraft_records': aircraft_count,
                'squadron_records': squadron_count,
                'mission_records': mission_count,
                'average_age_at_death': round(avg_age, 1) if avg_age else None,
                'average_missions_per_person': round(avg_missions, 1) if avg_missions else None,
                'decorated_personnel': decorated_personnel,
                'featured_personnel': featured_personnel,
                'squadron_distribution': squadron_distribution,
                'advanced_search_features': {
                    'date_range_filtering': True,
                    'aircraft_type_filtering': True,
                    'geographic_filtering': True,
                    'mission_count_filtering': True,
                    'awards_filtering': True,
                    'multi_criteria_search': True
                },
                'export_features': {
                    'pdf_memorial_reports': True,
                    'csv_personnel_export': True,
                    'csv_aircraft_export': True,
                    'advanced_search_export': True
                }
            })
            
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return jsonify({'error': 'Failed to get statistics', 'details': str(e)}), 500

# Serve the enhanced frontend with advanced search
@app.route('/')
def serve_frontend():
    """Serve the enhanced frontend with advanced search filters."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAF Bomber Command Research Database - Advanced Search & Export</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2c1810 0%, #1a0f08 50%, #0d0704 100%);
            color: #d4af37;
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            padding: 2rem 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 2px solid #d4af37;
        }
        
        .raf-badge {
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #d4af37, #f4e976);
            border-radius: 50%;
            margin: 0 auto 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        }
        
        .raf-star {
            font-size: 2rem;
            color: #2c1810;
            font-weight: bold;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .subtitle {
            font-size: 1.1rem;
            color: #b8860b;
            font-style: italic;
            margin-bottom: 1rem;
        }
        
        .enhanced-banner {
            background: linear-gradient(45deg, #d4af37, #f4e976);
            color: #2c1810;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-top: 1rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        .tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .tab {
            background: rgba(212, 175, 55, 0.1);
            border: 2px solid #d4af37;
            color: #d4af37;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .tab:hover, .tab.active {
            background: #d4af37;
            color: #2c1810;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(212, 175, 55, 0.3);
        }
        
        .tab-content {
            display: none;
            background: rgba(0, 0, 0, 0.4);
            padding: 2rem;
            border-radius: 15px;
            border: 1px solid #d4af37;
            backdrop-filter: blur(10px);
        }
        
        .tab-content.active {
            display: block;
        }
        
        .search-section {
            margin-bottom: 2rem;
        }
        
        .search-modes {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        .search-mode {
            padding: 0.5rem 1rem;
            background: rgba(212, 175, 55, 0.2);
            border: 1px solid #d4af37;
            border-radius: 15px;
            color: #d4af37;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .search-mode:hover, .search-mode.active {
            background: #d4af37;
            color: #2c1810;
        }
        
        .search-box {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        input[type="text"], input[type="date"], input[type="number"], select {
            padding: 0.75rem;
            border: 2px solid #d4af37;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.5);
            color: #d4af37;
            font-size: 1rem;
            min-width: 200px;
        }
        
        input[type="text"]:focus, input[type="date"]:focus, input[type="number"]:focus, select:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
        }
        
        .advanced-filters {
            display: none;
            background: rgba(0, 0, 0, 0.3);
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #d4af37;
            margin-bottom: 1rem;
        }
        
        .advanced-filters.active {
            display: block;
        }
        
        .filter-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .filter-label {
            font-weight: bold;
            color: #f4e976;
            font-size: 0.9rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: 2px solid #d4af37;
            border-radius: 8px;
            background: rgba(212, 175, 55, 0.1);
            color: #d4af37;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background: #d4af37;
            color: #2c1810;
            transform: translateY(-1px);
        }
        
        .btn-export {
            background: linear-gradient(45deg, #228B22, #32CD32);
            border-color: #228B22;
            color: white;
        }
        
        .btn-export:hover {
            background: linear-gradient(45deg, #32CD32, #228B22);
            color: white;
        }
        
        .btn-clear {
            background: linear-gradient(45deg, #DC143C, #FF6347);
            border-color: #DC143C;
            color: white;
        }
        
        .btn-clear:hover {
            background: linear-gradient(45deg, #FF6347, #DC143C);
            color: white;
        }
        
        .quick-buttons {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }
        
        .quick-btn {
            padding: 0.5rem 1rem;
            background: rgba(212, 175, 55, 0.2);
            border: 1px solid #d4af37;
            border-radius: 15px;
            color: #d4af37;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .quick-btn:hover {
            background: #d4af37;
            color: #2c1810;
        }
        
        .results {
            margin-top: 2rem;
        }
        
        .person-card {
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid #d4af37;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .person-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        }
        
        .person-name {
            font-size: 1.3rem;
            font-weight: bold;
            color: #f4e976;
            margin-bottom: 0.5rem;
        }
        
        .person-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .detail-item {
            color: #b8860b;
        }
        
        .detail-label {
            font-weight: bold;
            color: #d4af37;
        }
        
        .biography {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(212, 175, 55, 0.1);
            border-radius: 8px;
            border-left: 4px solid #d4af37;
        }
        
        .export-section {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(34, 139, 34, 0.1);
            border-radius: 8px;
            border: 1px solid #228B22;
        }
        
        .export-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #d4af37;
        }
        
        .error {
            background: rgba(220, 20, 60, 0.2);
            border: 1px solid #dc143c;
            color: #ff6b6b;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .success {
            background: rgba(34, 139, 34, 0.2);
            border: 1px solid #228B22;
            color: #90EE90;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid #d4af37;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #f4e976;
            display: block;
        }
        
        .stat-label {
            color: #b8860b;
            margin-top: 0.5rem;
        }
        
        .search-info {
            background: rgba(212, 175, 55, 0.1);
            border: 1px solid #d4af37;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 2rem; }
            .search-box { flex-direction: column; }
            input[type="text"], input[type="date"], input[type="number"], select { min-width: auto; }
            .tabs { flex-direction: column; }
            .person-details { grid-template-columns: 1fr; }
            .filter-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="raf-badge">
            <div class="raf-star">★</div>
        </div>
        <h1>RAF Bomber Command Research Database</h1>
        <p class="subtitle">Preserving the Memory of Those Who Served</p>
        <div class="enhanced-banner">🔍 Advanced Search & Export Features</div>
    </div>

    <div class="container">
        <div class="tabs">
            <div class="tab active" onclick="showTab('personnel')">Personnel Search</div>
            <div class="tab" onclick="showTab('aircraft')">Aircraft Database</div>
            <div class="tab" onclick="showTab('statistics')">Statistics</div>
        </div>

        <div id="personnel" class="tab-content active">
            <div class="search-section">
                <h2>Personnel Search</h2>
                
                <div class="search-modes">
                    <div class="search-mode active" onclick="toggleSearchMode('basic')">Basic Search</div>
                    <div class="search-mode" onclick="toggleSearchMode('advanced')">Advanced Filters</div>
                </div>
                
                <div class="search-box">
                    <input type="text" id="personnelSearch" placeholder="Search by name, service number, squadron, or role...">
                    <button class="btn" onclick="searchPersonnel()">Search</button>
                    <button class="btn btn-clear" onclick="clearSearch()">Clear</button>
                </div>
                
                <div id="advancedFilters" class="advanced-filters">
                    <h3>Advanced Search Filters</h3>
                    <div class="filter-grid">
                        <div class="filter-group">
                            <label class="filter-label">Date of Death Range</label>
                            <input type="date" id="dateFrom" placeholder="From">
                            <input type="date" id="dateTo" placeholder="To">
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Service Period</label>
                            <input type="date" id="serviceFrom" placeholder="Service Start">
                            <input type="date" id="serviceTo" placeholder="Service End">
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Aircraft Type</label>
                            <select id="aircraftType">
                                <option value="">All Aircraft Types</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Squadron</label>
                            <select id="squadronFilter">
                                <option value="">All Squadrons</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Role</label>
                            <select id="roleFilter">
                                <option value="">All Roles</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Rank</label>
                            <select id="rankFilter">
                                <option value="">All Ranks</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Base Location</label>
                            <select id="baseLocation">
                                <option value="">All Bases</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Age at Death</label>
                            <input type="number" id="ageFrom" placeholder="Min Age" min="18" max="50">
                            <input type="number" id="ageTo" placeholder="Max Age" min="18" max="50">
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Minimum Missions</label>
                            <input type="number" id="minMissions" placeholder="Min Missions" min="0" max="100">
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Awards</label>
                            <select id="hasAwards">
                                <option value="">All Personnel</option>
                                <option value="true">Decorated Personnel Only</option>
                                <option value="false">No Awards</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Memorial Location</label>
                            <select id="memorialLocation">
                                <option value="">All Memorial Locations</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="export-buttons">
                        <button class="btn" onclick="advancedSearch()">🔍 Apply Advanced Filters</button>
                        <button class="btn btn-clear" onclick="clearAdvancedFilters()">Clear All Filters</button>
                    </div>
                </div>
                
                <div class="quick-buttons">
                    <div class="quick-btn" onclick="quickSearch('Patrick Cassidy')">Patrick Cassidy</div>
                    <div class="quick-btn" onclick="quickSearch('Guy Gibson')">Guy Gibson</div>
                    <div class="quick-btn" onclick="quickSearch('97 Squadron')">97 Squadron</div>
                    <div class="quick-btn" onclick="quickSearch('617 Squadron')">617 Squadron</div>
                    <div class="quick-btn" onclick="quickSearch('Flight Engineer')">Flight Engineers</div>
                    <div class="quick-btn" onclick="quickSearch('Pathfinder')">Pathfinders</div>
                </div>
                
                <div class="export-section">
                    <h3>Export Options</h3>
                    <p>Export personnel data for research and memorial purposes</p>
                    <div class="export-buttons">
                        <button class="btn btn-export" onclick="exportAllPersonnelCSV()">📊 Export All Personnel (CSV)</button>
                        <button class="btn btn-export" onclick="exportSearchResultsCSV()">📋 Export Search Results (CSV)</button>
                    </div>
                </div>
            </div>
            
            <div id="personnelResults" class="results"></div>
        </div>

        <div id="aircraft" class="tab-content">
            <div class="search-section">
                <h2>Aircraft Database</h2>
                <div class="search-box">
                    <input type="text" id="aircraftSearch" placeholder="Search by aircraft ID, type, squadron, or manufacturer...">
                    <button class="btn" onclick="searchAircraft()">Search</button>
                </div>
                
                <div class="quick-buttons">
                    <div class="quick-btn" onclick="quickSearchAircraft('JB174')">JB174 (Patrick Cassidy)</div>
                    <div class="quick-btn" onclick="quickSearchAircraft('ED932')">ED932 (Guy Gibson)</div>
                    <div class="quick-btn" onclick="quickSearchAircraft('Lancaster')">Lancaster Aircraft</div>
                    <div class="quick-btn" onclick="quickSearchAircraft('Halifax')">Halifax Aircraft</div>
                </div>
                
                <div class="export-section">
                    <h3>Aircraft Export</h3>
                    <p>Export aircraft database for historical research</p>
                    <div class="export-buttons">
                        <button class="btn btn-export" onclick="exportAircraftCSV()">✈️ Export Aircraft Database (CSV)</button>
                    </div>
                </div>
            </div>
            
            <div id="aircraftResults" class="results"></div>
        </div>

        <div id="statistics" class="tab-content">
            <h2>Database Statistics</h2>
            <div id="statisticsContent" class="loading">Loading statistics...</div>
        </div>
    </div>

    <script>
        let currentSearchResults = [];
        let currentSearchMode = 'basic';
        let filterOptions = {};
        
        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            loadFilterOptions();
            loadStatistics();
        });
        
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Load statistics when statistics tab is selected
            if (tabName === 'statistics') {
                loadStatistics();
            }
        }
        
        function toggleSearchMode(mode) {
            currentSearchMode = mode;
            
            // Update search mode buttons
            document.querySelectorAll('.search-mode').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Show/hide advanced filters
            const advancedFilters = document.getElementById('advancedFilters');
            if (mode === 'advanced') {
                advancedFilters.classList.add('active');
            } else {
                advancedFilters.classList.remove('active');
            }
        }
        
        async function loadFilterOptions() {
            try {
                const response = await fetch('/api/filters/options');
                const data = await response.json();
                
                if (response.ok) {
                    filterOptions = data;
                    populateFilterDropdowns(data);
                }
            } catch (error) {
                console.error('Failed to load filter options:', error);
            }
        }
        
        function populateFilterDropdowns(options) {
            // Populate aircraft types
            const aircraftSelect = document.getElementById('aircraftType');
            options.aircraft_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                aircraftSelect.appendChild(option);
            });
            
            // Populate squadrons
            const squadronSelect = document.getElementById('squadronFilter');
            options.squadrons.forEach(squadron => {
                const option = document.createElement('option');
                option.value = squadron;
                option.textContent = squadron;
                squadronSelect.appendChild(option);
            });
            
            // Populate roles
            const roleSelect = document.getElementById('roleFilter');
            options.roles.forEach(role => {
                const option = document.createElement('option');
                option.value = role;
                option.textContent = role;
                roleSelect.appendChild(option);
            });
            
            // Populate ranks
            const rankSelect = document.getElementById('rankFilter');
            options.ranks.forEach(rank => {
                const option = document.createElement('option');
                option.value = rank;
                option.textContent = rank;
                rankSelect.appendChild(option);
            });
            
            // Populate base locations
            const baseSelect = document.getElementById('baseLocation');
            options.base_locations.forEach(base => {
                const option = document.createElement('option');
                option.value = base;
                option.textContent = base;
                baseSelect.appendChild(option);
            });
            
            // Populate memorial locations
            const memorialSelect = document.getElementById('memorialLocation');
            options.memorial_locations.forEach(memorial => {
                const option = document.createElement('option');
                option.value = memorial;
                option.textContent = memorial;
                memorialSelect.appendChild(option);
            });
        }
        
        function quickSearch(query) {
            document.getElementById('personnelSearch').value = query;
            searchPersonnel();
        }
        
        function quickSearchAircraft(query) {
            document.getElementById('aircraftSearch').value = query;
            searchAircraft();
        }
        
        function clearSearch() {
            document.getElementById('personnelSearch').value = '';
            document.getElementById('personnelResults').innerHTML = '';
            currentSearchResults = [];
        }
        
        function clearAdvancedFilters() {
            // Clear all filter inputs
            document.getElementById('dateFrom').value = '';
            document.getElementById('dateTo').value = '';
            document.getElementById('serviceFrom').value = '';
            document.getElementById('serviceTo').value = '';
            document.getElementById('aircraftType').value = '';
            document.getElementById('squadronFilter').value = '';
            document.getElementById('roleFilter').value = '';
            document.getElementById('rankFilter').value = '';
            document.getElementById('baseLocation').value = '';
            document.getElementById('ageFrom').value = '';
            document.getElementById('ageTo').value = '';
            document.getElementById('minMissions').value = '';
            document.getElementById('hasAwards').value = '';
            document.getElementById('memorialLocation').value = '';
            
            // Clear results
            document.getElementById('personnelResults').innerHTML = '';
            currentSearchResults = [];
        }
        
        async function searchPersonnel() {
            const query = document.getElementById('personnelSearch').value.trim();
            const resultsDiv = document.getElementById('personnelResults');
            
            if (!query && currentSearchMode === 'basic') {
                resultsDiv.innerHTML = '<div class="error">Please enter a search term</div>';
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading">Searching personnel records...</div>';
            
            try {
                const response = await fetch('/api/personnel/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Search failed');
                }
                
                currentSearchResults = data.results;
                displayPersonnelResults(data.results, query, 'basic');
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Search failed: ${error.message}</div>`;
            }
        }
        
        async function advancedSearch() {
            const resultsDiv = document.getElementById('personnelResults');
            resultsDiv.innerHTML = '<div class="loading">Applying advanced filters...</div>';
            
            try {
                // Collect all filter values
                const filters = {
                    query: document.getElementById('personnelSearch').value.trim(),
                    date_from: document.getElementById('dateFrom').value,
                    date_to: document.getElementById('dateTo').value,
                    service_from: document.getElementById('serviceFrom').value,
                    service_to: document.getElementById('serviceTo').value,
                    aircraft_type: document.getElementById('aircraftType').value,
                    squadron: document.getElementById('squadronFilter').value,
                    role: document.getElementById('roleFilter').value,
                    rank: document.getElementById('rankFilter').value,
                    base_location: document.getElementById('baseLocation').value,
                    age_from: document.getElementById('ageFrom').value,
                    age_to: document.getElementById('ageTo').value,
                    min_missions: document.getElementById('minMissions').value,
                    has_awards: document.getElementById('hasAwards').value,
                    memorial_location: document.getElementById('memorialLocation').value,
                    advanced_search: true
                };
                
                const response = await fetch('/api/personnel/search/advanced', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(filters)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Advanced search failed');
                }
                
                currentSearchResults = data.results;
                displayPersonnelResults(data.results, 'Advanced Search', 'advanced', data.filters_applied);
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Advanced search failed: ${error.message}</div>`;
            }
        }
        
        function displayPersonnelResults(results, query, searchType, filtersApplied = null) {
            const resultsDiv = document.getElementById('personnelResults');
            
            if (results.length === 0) {
                resultsDiv.innerHTML = `<div class="error">No personnel records found for "${query}"</div>`;
                return;
            }
            
            let html = `<div class="search-info">`;
            html += `<h3>Found ${results.length} personnel record(s)</h3>`;
            if (searchType === 'advanced' && filtersApplied) {
                html += `<p><strong>Advanced Search Applied:</strong> `;
                const activeFilters = Object.entries(filtersApplied)
                    .filter(([key, value]) => value && value !== '')
                    .map(([key, value]) => `${key.replace('_', ' ')}: ${value}`)
                    .join(', ');
                html += activeFilters || 'No specific filters';
                html += `</p>`;
            } else {
                html += `<p><strong>Search Query:</strong> "${query}"</p>`;
            }
            html += `</div>`;
            
            results.forEach(person => {
                html += `
                    <div class="person-card">
                        <div class="person-name">${person.name}</div>
                        <div class="person-details">
                            <div class="detail-item"><span class="detail-label">Service Number:</span> ${person.service_number}</div>
                            <div class="detail-item"><span class="detail-label">Rank:</span> ${person.rank}</div>
                            <div class="detail-item"><span class="detail-label">Role:</span> ${person.role}</div>
                            <div class="detail-item"><span class="detail-label">Squadron:</span> ${person.squadron}</div>
                            <div class="detail-item"><span class="detail-label">Aircraft:</span> ${person.aircraft_type || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Base:</span> ${person.base_location || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Age at Death:</span> ${person.age_at_death ? person.age_at_death + ' years' : 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Missions:</span> ${person.mission_count || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Memorial:</span> ${person.memorial_location || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Panel:</span> ${person.memorial_panel || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Awards:</span> ${person.awards || 'None recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Service Period:</span> ${person.service_start_date || 'Unknown'} - ${person.service_end_date || 'Unknown'}</div>
                        </div>
                        
                        ${person.biography ? `<div class="biography"><strong>Biography:</strong><br>${person.biography}</div>` : ''}
                        
                        <div class="export-section">
                            <h4>Memorial Export</h4>
                            <p>Generate professional memorial report for ${person.name}</p>
                            <div class="export-buttons">
                                <button class="btn btn-export" onclick="exportMemorialPDF('${person.service_number}', '${person.name}')">📄 Memorial Report (PDF)</button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
        
        async function searchAircraft() {
            const query = document.getElementById('aircraftSearch').value.trim();
            const resultsDiv = document.getElementById('aircraftResults');
            
            if (!query) {
                resultsDiv.innerHTML = '<div class="error">Please enter a search term</div>';
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading">Searching aircraft records...</div>';
            
            try {
                const response = await fetch('/api/aircraft/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Search failed');
                }
                
                displayAircraftResults(data.results, query);
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Search failed: ${error.message}</div>`;
            }
        }
        
        function displayAircraftResults(results, query) {
            const resultsDiv = document.getElementById('aircraftResults');
            
            if (results.length === 0) {
                resultsDiv.innerHTML = `<div class="error">No aircraft records found for "${query}"</div>`;
                return;
            }
            
            let html = `<h3>Found ${results.length} aircraft record(s) for "${query}"</h3>`;
            
            results.forEach(aircraft => {
                html += `
                    <div class="person-card">
                        <div class="person-name">${aircraft.aircraft_id} - ${aircraft.aircraft_type}</div>
                        <div class="person-details">
                            <div class="detail-item"><span class="detail-label">Squadron:</span> ${aircraft.squadron}</div>
                            <div class="detail-item"><span class="detail-label">Code:</span> ${aircraft.squadron_code || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Manufacturer:</span> ${aircraft.manufacturer || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Base:</span> ${aircraft.base_location || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">First Flight:</span> ${aircraft.first_flight_date || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Service Period:</span> ${aircraft.service_period_start || 'Unknown'} - ${aircraft.service_period_end || 'Unknown'}</div>
                            <div class="detail-item"><span class="detail-label">Service Days:</span> ${aircraft.service_days || 'Unknown'}</div>
                            <div class="detail-item"><span class="detail-label">Missions:</span> ${aircraft.missions_flown || 0}</div>
                            <div class="detail-item"><span class="detail-label">Fate:</span> ${aircraft.fate || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Notable Crew:</span> ${aircraft.notable_crew || 'Not recorded'}</div>
                        </div>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
        
        async function loadStatistics() {
            const statsDiv = document.getElementById('statisticsContent');
            
            try {
                const response = await fetch('/api/statistics');
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to load statistics');
                }
                
                let html = `
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="stat-number">${data.personnel_records}</span>
                            <div class="stat-label">Personnel Records</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">${data.aircraft_records}</span>
                            <div class="stat-label">Aircraft Records</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">${data.squadron_records}</span>
                            <div class="stat-label">Squadron Records</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">${data.mission_records}</span>
                            <div class="stat-label">Mission Records</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">${data.average_age_at_death || 'N/A'}</span>
                            <div class="stat-label">Average Age at Death</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">${data.average_missions_per_person || 'N/A'}</span>
                            <div class="stat-label">Average Missions</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">${data.decorated_personnel}</span>
                            <div class="stat-label">Decorated Personnel</div>
                        </div>
                    </div>
                    
                    <div class="export-section">
                        <h3>Advanced Search & Export Features</h3>
                        <p>Professional research capabilities with multi-criteria filtering and export options</p>
                        <div class="export-buttons">
                            <button class="btn btn-export" onclick="exportAllPersonnelCSV()">📊 Complete Personnel Database (CSV)</button>
                            <button class="btn btn-export" onclick="exportAircraftCSV()">✈️ Complete Aircraft Database (CSV)</button>
                        </div>
                    </div>
                `;
                
                if (data.featured_personnel && data.featured_personnel.length > 0) {
                    html += '<h3>Featured Personnel</h3>';
                    data.featured_personnel.forEach(person => {
                        html += `
                            <div class="person-card">
                                <div class="person-name">${person.name}</div>
                                <div class="person-details">
                                    <div class="detail-item"><span class="detail-label">Service Number:</span> ${person.service_number}</div>
                                    <div class="detail-item"><span class="detail-label">Rank:</span> ${person.rank}</div>
                                    <div class="detail-item"><span class="detail-label">Squadron:</span> ${person.squadron}</div>
                                    <div class="detail-item"><span class="detail-label">Missions:</span> ${person.mission_count || 'Not recorded'}</div>
                                    <div class="detail-item"><span class="detail-label">Base:</span> ${person.base_location || 'Not recorded'}</div>
                                </div>
                                <div class="export-section">
                                    <div class="export-buttons">
                                        <button class="btn btn-export" onclick="exportMemorialPDF('${person.service_number}', '${person.name}')">📄 Memorial Report (PDF)</button>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                }
                
                if (data.squadron_distribution && data.squadron_distribution.length > 0) {
                    html += '<h3>Squadron Distribution</h3>';
                    html += '<div class="stats-grid">';
                    data.squadron_distribution.forEach(squadron => {
                        html += `
                            <div class="stat-card">
                                <span class="stat-number">${squadron.count}</span>
                                <div class="stat-label">${squadron.squadron}</div>
                            </div>
                        `;
                    });
                    html += '</div>';
                }
                
                statsDiv.innerHTML = html;
                
            } catch (error) {
                statsDiv.innerHTML = `<div class="error">Failed to load statistics: ${error.message}</div>`;
            }
        }
        
        // Export Functions
        async function exportMemorialPDF(serviceNumber, name) {
            try {
                showMessage(`Generating memorial report for ${name}...`, 'loading');
                
                const response = await fetch(`/api/export/pdf/memorial/${serviceNumber}`);
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'PDF generation failed');
                }
                
                // Download the PDF
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `RAF_Memorial_Report_${name.replace(/\\s+/g, '_')}_${serviceNumber}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                showMessage(`Memorial report for ${name} downloaded successfully!`, 'success');
                
            } catch (error) {
                showMessage(`Failed to generate memorial report: ${error.message}`, 'error');
            }
        }
        
        async function exportAllPersonnelCSV() {
            try {
                showMessage('Generating complete personnel database export...', 'loading');
                
                const response = await fetch('/api/export/csv/personnel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'CSV export failed');
                }
                
                // Download the CSV
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'RAF_Personnel_Complete_Database_Advanced.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                showMessage('Personnel database exported successfully!', 'success');
                
            } catch (error) {
                showMessage(`Failed to export personnel database: ${error.message}`, 'error');
            }
        }
        
        async function exportSearchResultsCSV() {
            if (currentSearchResults.length === 0) {
                showMessage('No search results to export. Please perform a search first.', 'error');
                return;
            }
            
            try {
                let exportData = {};
                
                if (currentSearchMode === 'advanced') {
                    // Collect current filter values for advanced search export
                    exportData = {
                        query: document.getElementById('personnelSearch').value.trim(),
                        date_from: document.getElementById('dateFrom').value,
                        date_to: document.getElementById('dateTo').value,
                        service_from: document.getElementById('serviceFrom').value,
                        service_to: document.getElementById('serviceTo').value,
                        aircraft_type: document.getElementById('aircraftType').value,
                        squadron: document.getElementById('squadronFilter').value,
                        role: document.getElementById('roleFilter').value,
                        rank: document.getElementById('rankFilter').value,
                        base_location: document.getElementById('baseLocation').value,
                        age_from: document.getElementById('ageFrom').value,
                        age_to: document.getElementById('ageTo').value,
                        min_missions: document.getElementById('minMissions').value,
                        has_awards: document.getElementById('hasAwards').value,
                        memorial_location: document.getElementById('memorialLocation').value,
                        advanced_search: true
                    };
                    showMessage('Exporting advanced search results...', 'loading');
                } else {
                    const query = document.getElementById('personnelSearch').value.trim();
                    exportData = { query };
                    showMessage(`Exporting search results for "${query}"...`, 'loading');
                }
                
                const response = await fetch('/api/export/csv/personnel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(exportData)
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'CSV export failed');
                }
                
                // Download the CSV
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                if (currentSearchMode === 'advanced') {
                    a.download = 'RAF_Personnel_Advanced_Search_Results.csv';
                } else {
                    const query = exportData.query || 'Search';
                    a.download = `RAF_Personnel_Search_${query.replace(/\\s+/g, '_')}.csv`;
                }
                
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                showMessage('Search results exported successfully!', 'success');
                
            } catch (error) {
                showMessage(`Failed to export search results: ${error.message}`, 'error');
            }
        }
        
        async function exportAircraftCSV() {
            try {
                showMessage('Generating aircraft database export...', 'loading');
                
                const response = await fetch('/api/export/csv/aircraft');
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'CSV export failed');
                }
                
                // Download the CSV
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'RAF_Aircraft_Database_Advanced.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                showMessage('Aircraft database exported successfully!', 'success');
                
            } catch (error) {
                showMessage(`Failed to export aircraft database: ${error.message}`, 'error');
            }
        }
        
        function showMessage(message, type) {
            // Remove existing messages
            const existingMessages = document.querySelectorAll('.message-popup');
            existingMessages.forEach(msg => msg.remove());
            
            // Create new message
            const messageDiv = document.createElement('div');
            messageDiv.className = `message-popup ${type}`;
            messageDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                z-index: 1000;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            `;
            
            if (type === 'success') {
                messageDiv.style.background = 'rgba(34, 139, 34, 0.9)';
                messageDiv.style.color = 'white';
                messageDiv.style.border = '1px solid #228B22';
            } else if (type === 'error') {
                messageDiv.style.background = 'rgba(220, 20, 60, 0.9)';
                messageDiv.style.color = 'white';
                messageDiv.style.border = '1px solid #dc143c';
            } else {
                messageDiv.style.background = 'rgba(212, 175, 55, 0.9)';
                messageDiv.style.color = '#2c1810';
                messageDiv.style.border = '1px solid #d4af37';
            }
            
            messageDiv.textContent = message;
            document.body.appendChild(messageDiv);
            
            // Auto-remove after 5 seconds for success/error messages
            if (type !== 'loading') {
                setTimeout(() => {
                    if (messageDiv.parentNode) {
                        messageDiv.remove();
                    }
                }, 5000);
            }
        }
        
        // Handle Enter key in search boxes
        document.getElementById('personnelSearch').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                if (currentSearchMode === 'advanced') {
                    advancedSearch();
                } else {
                    searchPersonnel();
                }
            }
        });
        
        document.getElementById('aircraftSearch').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchAircraft();
            }
        });
    </script>
</body>
</html>'''

if __name__ == '__main__':
    try:
        # Initialize database
        initialize_database()
        
        logger.info(f"🎖️ RAF Bomber Command Research Database - Advanced Search & Export")
        logger.info(f"Memorial Database honoring Sergeant Patrick Cassidy and all RAF Bomber Command personnel")
        logger.info(f"Starting server on port {PORT}...")
        logger.info(f"Enhanced Features: Advanced Search Filters, PDF Memorial Reports, CSV Data Export")
        
        app.run(host='0.0.0.0', port=PORT, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)

