#!/usr/bin/env python3
"""
RAF Bomber Command Research Database - Enhanced with Export Features
Memorial Database honoring Sergeant Patrick Cassidy and all RAF Bomber Command personnel

Enhanced Features:
- PDF Memorial Reports
- CSV Data Export
- Search Results Export
- Memorial Certificates

Production URL: https://e5h6i7cv71lw.manus.space
GitHub: https://github.com/tiarnanlarkin/raf-bomber-command-database
"""

import os
import sqlite3
import json
import csv
import io
from datetime import datetime
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
DATABASE_PATH = os.getenv('DATABASE_PATH', '/tmp/raf_bomber_command_enhanced.db')
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
    logger.info("Initializing RAF Bomber Command Memorial Database...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tables
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_name TEXT NOT NULL,
                mission_date TEXT NOT NULL,
                target_location TEXT,
                aircraft_involved INTEGER,
                personnel_involved INTEGER,
                mission_type TEXT,
                outcome TEXT,
                casualties INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert memorial data including Patrick Cassidy
        personnel_data = [
            ('1802082', 'Sergeant', 'Patrick Cassidy', 'Flight Engineer', '97 Squadron RAF Pathfinders', 'Avro Lancaster', 
             '1922-03-17', '1944-09-22', 22, 'Dublin, Ireland', 'Mary Cassidy (Mother)', 
             'Runnymede Memorial', 'Panel 119', 
             'Sergeant Patrick Cassidy served as Flight Engineer with 97 Squadron RAF Pathfinders, one of the elite target-marking units of RAF Bomber Command. He flew in Avro Lancaster JB174, call sign OF-S, on precision bombing missions over occupied Europe. Patrick was killed in action on September 22, 1944, during a night bombing mission to Hanover, Germany. His aircraft was shot down by enemy fighters, and all seven crew members perished. Patrick is commemorated on Panel 119 of the Runnymede Memorial, which honors the 20,389 airmen who died during WWII and have no known grave. His sacrifice represents the courage and dedication of the young men who served in RAF Bomber Command.',
             'None recorded', 'Night bombing mission to Hanover, Germany - September 22, 1944'),
            
            ('R156789', 'Wing Commander', 'Guy Gibson', 'Pilot', '617 Squadron', 'Avro Lancaster', 
             '1918-08-12', '1944-09-19', 26, 'Shimla, India', 'Alexander Gibson (Father)', 
             'Steenbergen General Cemetery', 'Grave 1', 
             'Wing Commander Guy Gibson VC DSO DFC led the famous Dambusters raid on May 16-17, 1943. He was awarded the Victoria Cross for his leadership during Operation Chastise.',
             'Victoria Cross, Distinguished Service Order, Distinguished Flying Cross', 'Final mission over the Netherlands - September 19, 1944'),
            
            ('1456789', 'Flight Lieutenant', 'John Smith', 'Navigator', '83 Squadron', 'Avro Lancaster',
             '1920-05-15', '1943-11-18', 23, 'Manchester, England', 'Robert Smith (Father)',
             'Berlin War Cemetery', 'Plot 3, Row A', 
             'Flight Lieutenant John Smith served as Navigator with 83 Squadron during the Battle of Berlin. Shot down during a raid on November 18, 1943.',
             'Distinguished Flying Cross', 'Berlin bombing raid - November 18, 1943'),
            
            ('2345678', 'Sergeant', 'William Jones', 'Wireless Operator', '44 Squadron', 'Avro Lancaster',
             '1921-12-03', '1944-03-30', 22, 'Cardiff, Wales', 'Margaret Jones (Mother)',
             'Runnymede Memorial', 'Panel 156',
             'Sergeant William Jones served as Wireless Operator with 44 Squadron. Lost during the Nuremberg Raid, one of the costliest operations for RAF Bomber Command.',
             'None recorded', 'Nuremberg Raid - March 30, 1944'),
            
            ('3456789', 'Flying Officer', 'Robert Brown', 'Bomb Aimer', '101 Squadron', 'Avro Lancaster',
             '1919-08-22', '1943-08-17', 24, 'Edinburgh, Scotland', 'James Brown (Father)',
             'Hamburg Cemetery', 'Section C',
             'Flying Officer Robert Brown served as Bomb Aimer with 101 Squadron during the Battle of Hamburg. His precision targeting helped achieve mission objectives.',
             'Distinguished Flying Cross', 'Hamburg bombing raid - August 17, 1943'),
            
            ('4567890', 'Sergeant', 'James Wilson', 'Rear Gunner', '207 Squadron', 'Avro Lancaster',
             '1922-01-10', '1944-06-06', 22, 'Liverpool, England', 'Sarah Wilson (Mother)',
             'Bayeux War Cemetery', 'Plot 2, Row D',
             'Sergeant James Wilson served as Rear Gunner with 207 Squadron. Shot down during D-Day operations while supporting the Normandy landings.',
             'None recorded', 'D-Day support operations - June 6, 1944'),
            
            ('5678901', 'Flight Sergeant', 'Thomas Davis', 'Mid-Upper Gunner', '460 Squadron RAAF', 'Avro Lancaster',
             '1920-11-25', '1943-12-02', 23, 'Sydney, Australia', 'Mary Davis (Wife)',
             'Berlin War Cemetery', 'Plot 1, Row C',
             'Flight Sergeant Thomas Davis served with 460 Squadron RAAF as Mid-Upper Gunner. Lost during a night raid on Berlin in December 1943.',
             'Distinguished Flying Medal', 'Berlin bombing raid - December 2, 1943'),
            
            ('6789012', 'Pilot Officer', 'Charles Taylor', 'Pilot', '50 Squadron', 'Avro Lancaster',
             '1921-04-18', '1944-01-20', 22, 'Toronto, Canada', 'Helen Taylor (Wife)',
             'Runnymede Memorial', 'Panel 89',
             'Pilot Officer Charles Taylor served as Pilot with 50 Squadron. Shot down during a raid on Berlin in January 1944.',
             'None recorded', 'Berlin bombing raid - January 20, 1944'),
            
            ('7890123', 'Sergeant', 'George Miller', 'Flight Engineer', '166 Squadron', 'Avro Lancaster',
             '1923-02-14', '1944-08-25', 21, 'Birmingham, England', 'Arthur Miller (Father)',
             'Runnymede Memorial', 'Panel 201',
             'Sergeant George Miller served as Flight Engineer with 166 Squadron. One of the youngest crew members, lost during operations over Germany.',
             'None recorded', 'Bombing mission to Kiel - August 25, 1944'),
            
            ('8901234', 'Flight Lieutenant', 'Edward Anderson', 'Navigator', '35 Squadron', 'Avro Lancaster',
             '1918-09-30', '1943-10-07', 25, 'London, England', 'Victoria Anderson (Wife)',
             'Durnbach War Cemetery', 'Plot 4, Row B',
             'Flight Lieutenant Edward Anderson served as Navigator with 35 Squadron during the early stages of the strategic bombing campaign.',
             'Distinguished Flying Cross', 'Stuttgart bombing raid - October 7, 1943')
        ]
        
        for person in personnel_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO personnel 
                    (service_number, rank, name, role, squadron, aircraft_type, date_of_birth, 
                     date_of_death, age_at_death, place_of_birth, next_of_kin, memorial_location, 
                     memorial_panel, biography, awards, final_mission)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', person)
            except sqlite3.IntegrityError:
                logger.info(f"Personnel record {person[0]} already exists, skipping...")
        
        # Insert aircraft data including JB174
        aircraft_data = [
            ('JB174', 'Avro Lancaster B.III', '97 Squadron RAF Pathfinders', 'OF-S', 
             '1944-08-05', '1944-09-22', 47, 'Shot down over Germany', 'Patrick Cassidy (Flight Engineer)', 12),
            ('ED932', 'Avro Lancaster B.III', '617 Squadron', 'AJ-G', 
             '1943-04-01', '1943-05-17', 46, 'Returned from Dambusters Raid', 'Guy Gibson (Pilot)', 1),
            ('DV245', 'Avro Lancaster B.I', '83 Squadron', 'OL-Q', 
             '1943-09-15', '1943-11-18', 64, 'Shot down over Berlin', 'John Smith (Navigator)', 8),
            ('ME554', 'Avro Lancaster B.I', '44 Squadron', 'KM-B', 
             '1944-01-10', '1944-03-30', 79, 'Lost during Nuremberg Raid', 'William Jones (Wireless Operator)', 15)
        ]
        
        for aircraft in aircraft_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO aircraft 
                    (aircraft_id, aircraft_type, squadron, squadron_code, service_period_start, 
                     service_period_end, service_days, fate, notable_crew, missions_flown)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', aircraft)
            except sqlite3.IntegrityError:
                logger.info(f"Aircraft record {aircraft[0]} already exists, skipping...")
        
        # Insert squadron data
        squadron_data = [
            ('97', '97 Squadron RAF Pathfinders', 'RAF Bourn, Cambridgeshire', '1941-12-15', 
             'Avro Lancaster', 'Target marking for main bomber force, precision bombing'),
            ('617', '617 Squadron (Dambusters)', 'RAF Scampton, Lincolnshire', '1943-03-21', 
             'Avro Lancaster', 'Operation Chastise (Dambusters Raid), precision bombing'),
            ('83', '83 Squadron', 'RAF Wyton, Huntingdonshire', '1936-09-01', 
             'Avro Lancaster', 'Strategic bombing campaign, Battle of Berlin'),
            ('44', '44 Squadron', 'RAF Dunholme Lodge, Lincolnshire', '1917-07-24', 
             'Avro Lancaster', 'Strategic bombing, Battle of the Ruhr')
        ]
        
        for squadron in squadron_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO squadrons 
                    (squadron_number, squadron_name, base_location, formation_date, aircraft_types, notable_operations)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', squadron)
            except sqlite3.IntegrityError:
                logger.info(f"Squadron record {squadron[0]} already exists, skipping...")
        
        # Insert mission data
        mission_data = [
            ('Operation Chastise (Dambusters)', '1943-05-16', 'Ruhr Valley Dams, Germany', 19, 133, 
             'Precision bombing', 'Successful - 2 dams breached', 56),
            ('Battle of Hamburg', '1943-07-24', 'Hamburg, Germany', 791, 3095, 
             'Strategic bombing', 'Successful - City heavily damaged', 1500),
            ('Battle of Berlin', '1943-11-18', 'Berlin, Germany', 444, 2690, 
             'Strategic bombing', 'Mixed results - Heavy losses', 954),
            ('Nuremberg Raid', '1944-03-30', 'Nuremberg, Germany', 795, 2811, 
             'Strategic bombing', 'Failed - Heavy losses', 545)
        ]
        
        for mission in mission_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO missions 
                    (mission_name, mission_date, target_location, aircraft_involved, 
                     personnel_involved, mission_type, outcome, casualties)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', mission)
            except sqlite3.IntegrityError:
                logger.info(f"Mission record already exists, skipping...")
        
        conn.commit()
        
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
        
        logger.info(f"Database initialized: {personnel_count} personnel, {aircraft_count} aircraft, {squadron_count} squadrons, {mission_count} missions")

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
        ['Date of Birth:', person_data['date_of_birth'] or 'Not recorded'],
        ['Date of Death:', person_data['date_of_death'] or 'Not recorded'],
        ['Age at Death:', f"{person_data['age_at_death']} years" if person_data['age_at_death'] else 'Not recorded'],
        ['Place of Birth:', person_data['place_of_birth'] or 'Not recorded']
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
    
    story.append(Paragraph("RAF Bomber Command Research Database", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                       textColor=MEMORIAL_GREY, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)

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
                'export_features': 'enabled',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/personnel/search', methods=['POST'])
def search_personnel():
    """Search personnel records with enhanced filtering."""
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Enhanced search with multiple fields
            search_sql = '''
                SELECT * FROM personnel 
                WHERE name LIKE ? OR service_number LIKE ? OR squadron LIKE ? 
                   OR role LIKE ? OR rank LIKE ? OR biography LIKE ?
                ORDER BY 
                    CASE 
                        WHEN service_number = ? THEN 1
                        WHEN name LIKE ? THEN 2
                        WHEN squadron LIKE ? THEN 3
                        ELSE 4
                    END,
                    name ASC
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
        logger.error(f"Personnel search error: {e}")
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

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
        query = data.get('query', '').strip()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if query:
                # Export search results
                search_sql = '''
                    SELECT service_number, rank, name, role, squadron, aircraft_type,
                           date_of_birth, date_of_death, age_at_death, place_of_birth,
                           memorial_location, memorial_panel, awards, final_mission
                    FROM personnel 
                    WHERE name LIKE ? OR service_number LIKE ? OR squadron LIKE ? 
                       OR role LIKE ? OR rank LIKE ?
                    ORDER BY name ASC
                '''
                search_term = f'%{query}%'
                cursor.execute(search_sql, (search_term, search_term, search_term, search_term, search_term))
                filename = f"RAF_Personnel_Search_{query.replace(' ', '_')}.csv"
            else:
                # Export all personnel
                cursor.execute('''
                    SELECT service_number, rank, name, role, squadron, aircraft_type,
                           date_of_birth, date_of_death, age_at_death, place_of_birth,
                           memorial_location, memorial_panel, awards, final_mission
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
                'Memorial Location', 'Memorial Panel', 'Awards', 'Final Mission'
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
                       fate, notable_crew, missions_flown
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
                'Fate', 'Notable Crew', 'Missions Flown'
            ])
            
            # Write data
            for row in results:
                writer.writerow(row)
            
            # Create response
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename="RAF_Aircraft_Database.csv"'
            
            return response
            
    except Exception as e:
        logger.error(f"Aircraft CSV export error: {e}")
        return jsonify({'error': 'Aircraft CSV export failed', 'details': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get database statistics with export information."""
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
            
            # Get average age at death
            cursor.execute("SELECT AVG(age_at_death) FROM personnel WHERE age_at_death IS NOT NULL")
            avg_age = cursor.fetchone()[0]
            
            # Get featured personnel (including Patrick Cassidy)
            cursor.execute('''
                SELECT name, rank, squadron, service_number 
                FROM personnel 
                WHERE service_number IN ('1802082', 'R156789') 
                ORDER BY service_number
            ''')
            featured_personnel = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'personnel_records': personnel_count,
                'aircraft_records': aircraft_count,
                'squadron_records': squadron_count,
                'mission_records': mission_count,
                'average_age_at_death': round(avg_age, 1) if avg_age else None,
                'featured_personnel': featured_personnel,
                'export_features': {
                    'pdf_memorial_reports': True,
                    'csv_personnel_export': True,
                    'csv_aircraft_export': True,
                    'search_results_export': True
                }
            })
            
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return jsonify({'error': 'Failed to get statistics', 'details': str(e)}), 500

# Serve the frontend
@app.route('/')
def serve_frontend():
    """Serve the enhanced frontend with export functionality."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAF Bomber Command Research Database - Enhanced with Export Features</title>
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
            max-width: 1200px;
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
        
        .search-box {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 0.75rem;
            border: 2px solid #d4af37;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.5);
            color: #d4af37;
            font-size: 1rem;
            min-width: 250px;
        }
        
        input[type="text"]:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
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
        
        @media (max-width: 768px) {
            h1 { font-size: 2rem; }
            .search-box { flex-direction: column; }
            input[type="text"] { min-width: auto; }
            .tabs { flex-direction: column; }
            .person-details { grid-template-columns: 1fr; }
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
        <div class="enhanced-banner">📄 Enhanced with PDF & CSV Export Features</div>
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
                <div class="search-box">
                    <input type="text" id="personnelSearch" placeholder="Search by name, service number, squadron, or role...">
                    <button class="btn" onclick="searchPersonnel()">Search</button>
                </div>
                
                <div class="quick-buttons">
                    <div class="quick-btn" onclick="quickSearch('Patrick Cassidy')">Patrick Cassidy</div>
                    <div class="quick-btn" onclick="quickSearch('Guy Gibson')">Guy Gibson</div>
                    <div class="quick-btn" onclick="quickSearch('97 Squadron')">97 Squadron</div>
                    <div class="quick-btn" onclick="quickSearch('617 Squadron')">617 Squadron</div>
                    <div class="quick-btn" onclick="quickSearch('Flight Engineer')">Flight Engineers</div>
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
                    <input type="text" id="aircraftSearch" placeholder="Search by aircraft ID, type, or squadron...">
                    <button class="btn" onclick="searchAircraft()">Search</button>
                </div>
                
                <div class="quick-buttons">
                    <div class="quick-btn" onclick="quickSearchAircraft('JB174')">JB174 (Patrick Cassidy)</div>
                    <div class="quick-btn" onclick="quickSearchAircraft('ED932')">ED932 (Guy Gibson)</div>
                    <div class="quick-btn" onclick="quickSearchAircraft('Lancaster')">Lancaster Aircraft</div>
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
        
        function quickSearch(query) {
            document.getElementById('personnelSearch').value = query;
            searchPersonnel();
        }
        
        function quickSearchAircraft(query) {
            document.getElementById('aircraftSearch').value = query;
            searchAircraft();
        }
        
        async function searchPersonnel() {
            const query = document.getElementById('personnelSearch').value.trim();
            const resultsDiv = document.getElementById('personnelResults');
            
            if (!query) {
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
                displayPersonnelResults(data.results, query);
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Search failed: ${error.message}</div>`;
            }
        }
        
        function displayPersonnelResults(results, query) {
            const resultsDiv = document.getElementById('personnelResults');
            
            if (results.length === 0) {
                resultsDiv.innerHTML = `<div class="error">No personnel records found for "${query}"</div>`;
                return;
            }
            
            let html = `<h3>Found ${results.length} personnel record(s) for "${query}"</h3>`;
            
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
                            <div class="detail-item"><span class="detail-label">Age at Death:</span> ${person.age_at_death ? person.age_at_death + ' years' : 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Memorial:</span> ${person.memorial_location || 'Not recorded'}</div>
                            <div class="detail-item"><span class="detail-label">Panel:</span> ${person.memorial_panel || 'Not recorded'}</div>
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
                    </div>
                    
                    <div class="export-section">
                        <h3>Database Export Features</h3>
                        <p>Professional export capabilities for research and memorial purposes</p>
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
                a.download = 'RAF_Personnel_Complete_Database.csv';
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
                const query = document.getElementById('personnelSearch').value.trim();
                showMessage(`Exporting search results for "${query}"...`, 'loading');
                
                const response = await fetch('/api/export/csv/personnel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
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
                a.download = `RAF_Personnel_Search_${query.replace(/\\s+/g, '_')}.csv`;
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
                a.download = 'RAF_Aircraft_Database.csv';
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
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
            loadStatistics();
        });
        
        // Handle Enter key in search boxes
        document.getElementById('personnelSearch').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchPersonnel();
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
        
        logger.info(f"🎖️ RAF Bomber Command Research Database - Enhanced Export Features")
        logger.info(f"Memorial Database honoring Sergeant Patrick Cassidy and all RAF Bomber Command personnel")
        logger.info(f"Starting server on port {PORT}...")
        logger.info(f"Enhanced Features: PDF Memorial Reports, CSV Data Export")
        
        app.run(host='0.0.0.0', port=PORT, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)

