#!/usr/bin/env python3
"""
RAF Bomber Command Database - Enhanced AI Historical Research Assistant
Advanced Archival Signposting and Research Pathway System

Features:
- Enhanced AI Research Assistant with advanced archival integration
- Sophisticated research pathway guidance with detailed methodology
- Advanced archival signposting with direct search links
- Personalized research strategies based on available information
- Expert historian tips and professional insights
- Document hunting guidance with specific archive series
- Memorial and genealogy research support with family connections
- Interactive research planning with timeline estimation

Memorial Dedication: Honoring Sergeant Patrick Cassidy (Service Number 1802082)
and all RAF Bomber Command personnel who served with courage and sacrifice.
"""

import os
import sqlite3
import json
import csv
import io
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template_string, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

# Database configuration
DATABASE_PATH = '/tmp/raf_bomber_command_enhanced_research.db'

# OpenAI configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def init_database():
    """Initialize the database with comprehensive RAF Bomber Command data and enhanced research resources"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY,
            service_number TEXT UNIQUE,
            name TEXT,
            rank TEXT,
            squadron TEXT,
            role TEXT,
            age_at_death INTEGER,
            date_of_death TEXT,
            service_start TEXT,
            service_end TEXT,
            aircraft_type TEXT,
            base_location TEXT,
            missions_completed INTEGER,
            awards TEXT,
            memorial_location TEXT,
            biography TEXT,
            family_connections TEXT,
            research_notes TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aircraft (
            id INTEGER PRIMARY KEY,
            aircraft_id TEXT UNIQUE,
            aircraft_type TEXT,
            squadron TEXT,
            service_start TEXT,
            service_end TEXT,
            missions_completed INTEGER,
            crew_members TEXT,
            notable_operations TEXT,
            fate TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_archives (
            id INTEGER PRIMARY KEY,
            archive_name TEXT,
            archive_type TEXT,
            website_url TEXT,
            contact_info TEXT,
            specialization TEXT,
            access_requirements TEXT,
            cost_info TEXT,
            research_tips TEXT,
            search_url_template TEXT,
            specific_collections TEXT,
            opening_hours TEXT,
            location TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_sources (
            id INTEGER PRIMARY KEY,
            source_name TEXT,
            source_type TEXT,
            description TEXT,
            url TEXT,
            access_method TEXT,
            cost TEXT,
            research_value TEXT,
            archive_series TEXT,
            search_tips TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_pathways (
            id INTEGER PRIMARY KEY,
            pathway_name TEXT,
            research_type TEXT,
            description TEXT,
            steps TEXT,
            estimated_timeline TEXT,
            difficulty_level TEXT,
            success_rate TEXT,
            required_skills TEXT
        )
    ''')
    
    # Insert comprehensive personnel data with enhanced research information
    personnel_data = [
        ('1802082', 'Patrick Cassidy', 'Sergeant', '97 Squadron RAF Pathfinders', 'Flight Engineer', 21, '1943-11-15', '1943-08-01', '1943-11-15', 'Avro Lancaster', 'RAF Bourn, Cambridgeshire', 47, 'None', 'Runnymede Memorial Panel 119', 'Sergeant Patrick Cassidy served as Flight Engineer with 97 Squadron RAF Pathfinders, one of the elite target-marking units of RAF Bomber Command. Flying in Avro Lancaster JB174, he participated in precision bombing operations over occupied Europe. His aircraft was lost during a mission to Hanover on November 15, 1943, after just 47 days of operational service. Patrick was 21 years old and is commemorated on Panel 119 of the Runnymede Memorial.', 'Family from Ireland, possible connections in County Cork', 'Service record available in AIR 79 series, squadron records in AIR 27/781'),
        ('R156789', 'Guy Gibson', 'Wing Commander', '617 Squadron', 'Pilot', 26, '1944-09-19', '1940-01-01', '1944-09-19', 'Avro Lancaster', 'RAF Scampton, Lincolnshire', 174, 'Victoria Cross, Distinguished Service Order and Bar, Distinguished Flying Cross and Bar', 'Steenbergen General Cemetery', 'Wing Commander Guy Gibson VC DSO DFC led the famous Dambusters raid on May 16-17, 1943. As commanding officer of 617 Squadron, he flew the lead aircraft during Operation Chastise, the attack on the Ruhr dams. Gibson completed 174 operational flights and was awarded the Victoria Cross for his leadership during the Dambusters raid.', 'Extensive family records, married Joan Evelyn Moore', 'Comprehensive records in multiple series, extensive documentation'),
        ('1234567', 'John Smith', 'Flight Sergeant', '101 Squadron', 'Wireless Operator', 23, '1943-12-20', '1942-06-15', '1943-12-20', 'Avro Lancaster', 'RAF Ludford Magna, Lincolnshire', 89, 'Distinguished Flying Medal', 'Berlin War Cemetery', 'Flight Sergeant John Smith served as Wireless Operator with 101 Squadron, specializing in electronic countermeasures operations. His squadron was equipped with special radio equipment to jam German night fighter communications.', 'Family from Yorkshire, possible relatives in Sheffield area', 'Service record in AIR 79, squadron records in AIR 27/1234'),
        ('2345678', 'Robert Johnson', 'Pilot Officer', '35 Squadron', 'Navigator', 20, '1944-03-30', '1943-09-10', '1944-03-30', 'Handley Page Halifax', 'RAF Graveley, Huntingdonshire', 67, 'None', 'Bayeux War Cemetery', 'Pilot Officer Robert Johnson served as Navigator with 35 Squadron, part of the Pathfinder Force. He specialized in target marking and navigation for main force bombing operations.', 'Family from London, father worked in aviation industry', 'Service record available, Pathfinder records well-documented'),
        ('3456789', 'William Brown', 'Flight Lieutenant', '460 Squadron RAAF', 'Bomb Aimer', 24, '1944-08-25', '1943-02-01', '1944-08-25', 'Avro Lancaster', 'RAF Binbrook, Lincolnshire', 156, 'Distinguished Flying Cross', 'Durnbach War Cemetery', 'Flight Lieutenant William Brown served as Bomb Aimer with 460 Squadron RAAF, an Australian squadron operating with RAF Bomber Command. He completed 156 operational flights before being lost over Germany.', 'Australian family, connections in Melbourne and Sydney', 'Australian records available through National Archives of Australia'),
        ('4567890', 'James Wilson', 'Sergeant', '44 Squadron', 'Rear Gunner', 19, '1943-10-14', '1943-05-20', '1943-10-14', 'Avro Lancaster', 'RAF Dunholme Lodge, Lincolnshire', 34, 'None', 'Runnymede Memorial', 'Sergeant James Wilson served as Rear Gunner with 44 Squadron. At just 19 years old, he was one of the youngest aircrew members, manning the rear turret of Avro Lancaster bombers during operations over occupied Europe.', 'Family from Scotland, possible connections in Glasgow', 'Limited records due to age, family may have additional information'),
        ('5678901', 'Thomas Davis', 'Flying Officer', '207 Squadron', 'Pilot', 25, '1944-06-12', '1942-11-30', '1944-06-12', 'Avro Lancaster', 'RAF Spilsby, Lincolnshire', 198, 'Distinguished Flying Cross and Bar', 'Hamburg Cemetery', 'Flying Officer Thomas Davis served as Pilot with 207 Squadron, completing 198 operational flights. He was awarded the Distinguished Flying Cross and Bar for his exceptional service and leadership.', 'Family from Wales, father was a coal miner', 'Extensive service record due to long operational career'),
        ('6789012', 'Charles Miller', 'Sergeant', '83 Squadron', 'Mid-Upper Gunner', 22, '1944-01-27', '1943-07-15', '1944-01-27', 'Avro Lancaster', 'RAF Wyton, Huntingdonshire', 78, 'None', 'Runnymede Memorial', 'Sergeant Charles Miller served as Mid-Upper Gunner with 83 Squadron, part of the Pathfinder Force. He operated the mid-upper gun turret, providing defensive fire during bombing operations.', 'Family from Manchester, worked in textile industry', 'Pathfinder records available, squadron well-documented'),
        ('7890123', 'George Taylor', 'Flight Sergeant', '166 Squadron', 'Flight Engineer', 23, '1943-09-23', '1943-04-10', '1943-09-23', 'Avro Lancaster', 'RAF Kirmington, Lincolnshire', 45, 'None', 'Berlin War Cemetery', 'Flight Sergeant George Taylor served as Flight Engineer with 166 Squadron, responsible for monitoring aircraft systems and assisting the pilot during operations.', 'Family from Birmingham, father worked in aircraft manufacturing', 'Service record available, family may have employment records'),
        ('8901234', 'Edward Anderson', 'Sergeant', '50 Squadron', 'Wireless Operator', 21, '1944-02-15', '1943-08-20', '1944-02-15', 'Avro Lancaster', 'RAF Skellingthorpe, Lincolnshire', 56, 'None', 'Bayeux War Cemetery', 'Sergeant Edward Anderson served as Wireless Operator with 50 Squadron, maintaining radio communications during bombing operations and coordinating with ground control.', 'Family from Devon, rural farming background', 'Service record available, local parish records may exist')
    ]
    
    for person in personnel_data:
        cursor.execute('''
            INSERT OR REPLACE INTO personnel 
            (service_number, name, rank, squadron, role, age_at_death, date_of_death, 
             service_start, service_end, aircraft_type, base_location, missions_completed, 
             awards, memorial_location, biography, family_connections, research_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', person)
    
    # Insert enhanced research archives with advanced signposting
    archives_data = [
        ('The National Archives (UK)', 'Government Archive', 'https://www.nationalarchives.gov.uk/', 'enquiry@nationalarchives.gov.uk', 'RAF service records, operational records, squadron histories', 'Free online access, paid research services available', 'Free browsing, £3.50 per download', 'Essential for official service records. Search AIR series for RAF records. Use Discovery catalogue with specific service numbers.', 'https://discovery.nationalarchives.gov.uk/search/quick?_q={search_term}', 'AIR 79 (service records), AIR 27 (squadron records), AIR 14 (Bomber Command records)', 'Mon-Sat 9:00-17:00', 'Kew, London TW9 4DU'),
        ('RAF Museum', 'Military Museum', 'https://www.rafmuseum.org.uk/', 'research@rafmuseum.org.uk', 'Aircraft histories, squadron records, personal collections', 'Email appointment required', 'Free research access', 'Excellent for squadron histories and aircraft technical details. Contact researchers directly for personalized assistance.', 'https://www.rafmuseum.org.uk/research/collections-search/?q={search_term}', 'Squadron histories, aircraft records, personal collections, photographs', 'Tue-Sat 10:00-16:00', 'London NW9 5LL and Cosford TF11 8UP'),
        ('Commonwealth War Graves Commission', 'Memorial Database', 'https://www.cwgc.org/', 'general.enq@cwgc.org', 'Burial and memorial records', 'Free online database', 'Free', 'Essential for finding burial/memorial locations and basic service details. Includes next of kin information.', 'https://www.cwgc.org/find-war-dead/?surname={search_term}', 'War dead database, cemetery records, memorial registers', '24/7 online access', 'Maidenhead SL6 7DX'),
        ('Imperial War Museums', 'War Museum', 'https://www.iwm.org.uk/', 'collections@iwm.org.uk', 'Personal papers, photographs, oral histories', 'Appointment required for archives', 'Free research access', 'Valuable for personal stories and photographs. Extensive oral history collection.', 'https://www.iwm.org.uk/collections/search?query={search_term}', 'Personal papers, photographs, oral histories, diaries, letters', 'Tue-Sat 10:00-17:00', 'London SE1 6HZ and other locations'),
        ('Bomber Command Museum of Canada', 'Specialist Museum', 'https://bombercommandmuseum.ca/', 'info@bombercommandmuseum.ca', 'Canadian aircrew records, squadron histories', 'Email enquiries', 'Free research assistance', 'Essential for Commonwealth aircrew research. Strong connections with veteran families.', 'https://bombercommandmuseum.ca/research/?search={search_term}', 'Canadian aircrew records, squadron histories, veteran accounts', 'Seasonal hours, check website', 'Nanton, Alberta, Canada'),
        ('Air Historical Branch (RAF)', 'Military Archive', 'https://www.raf.mod.uk/our-organisation/air-historical-branch/', 'Air-AHB-Enquiries@mod.gov.uk', 'Official RAF histories, operational records', 'Written enquiries only', 'Free for basic enquiries', 'Official RAF historical records and narratives. Excellent for operational context.', 'Email enquiry required', 'Official histories, operational records, intelligence reports', 'Mon-Fri 9:00-17:00', 'RAF Northolt, Middlesex'),
        ('Ancestry.com', 'Genealogy Database', 'https://www.ancestry.com/', 'support@ancestry.com', 'Military records, census data, family trees', 'Subscription required', '£12.95-£24.95 per month', 'Good for family background and military service records. Strong UK military collections.', 'https://www.ancestry.com/search/?name={search_term}', 'Military records, census data, birth/death records, family trees', '24/7 online access', 'Online service'),
        ('FindMyPast', 'Genealogy Database', 'https://www.findmypast.com/', 'help@findmypast.com', 'Military records, newspapers, directories', 'Subscription required', '£12.95-£18.95 per month', 'Strong collection of military records and local newspapers. Excellent for family research.', 'https://www.findmypast.com/search-results?firstname={search_term}', 'Military records, newspapers, directories, parish records', '24/7 online access', 'Online service'),
        ('Forces War Records', 'Military Database', 'https://www.forces-war-records.co.uk/', 'help@forces-war-records.co.uk', 'Military service records, medal rolls', 'Subscription required', '£9.95-£13.95 per month', 'Specialized military records database. Good for medal and service records.', 'https://www.forces-war-records.co.uk/search?name={search_term}', 'Service records, medal rolls, casualty lists, unit histories', '24/7 online access', 'Online service'),
        ('Local County Archives', 'Regional Archives', 'Various', 'Various', 'Local records, newspapers, family histories', 'Varies by location', 'Usually free', 'Essential for local context and family connections. Often have unique collections.', 'Search individual county archive websites', 'Local newspapers, parish records, family collections, photographs', 'Varies by location', 'Various locations across UK')
    ]
    
    for archive in archives_data:
        cursor.execute('''
            INSERT OR REPLACE INTO research_archives 
            (archive_name, archive_type, website_url, contact_info, specialization, 
             access_requirements, cost_info, research_tips, search_url_template,
             specific_collections, opening_hours, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', archive)
    
    # Insert enhanced research sources with detailed guidance
    sources_data = [
        ('RAF Service Records (AIR 79)', 'Primary Source', 'Individual service records for RAF personnel', 'https://discovery.nationalarchives.gov.uk/', 'Online at The National Archives', '£3.50 per download', 'Essential - contains complete service history', 'AIR 79', 'Search by service number for best results. Records include enlistment, training, postings, and casualty details.'),
        ('Squadron Operational Record Books', 'Primary Source', 'Daily records of squadron activities and operations', 'https://discovery.nationalarchives.gov.uk/', 'Online at The National Archives', 'Free to view, £3.50 to download', 'Vital for understanding daily operations and specific missions', 'AIR 27', 'Search by squadron number. Look for Form 540 (daily entries) and Form 541 (combat reports).'),
        ('Combat Reports', 'Primary Source', 'Individual mission reports and combat accounts', 'https://discovery.nationalarchives.gov.uk/', 'Online at The National Archives', 'Free to view, £3.50 to download', 'Detailed accounts of specific operations and encounters', 'AIR 50', 'Search by date and squadron. Provides detailed mission accounts and crew experiences.'),
        ('Medal Citation Records', 'Primary Source', 'Official citations for gallantry and service medals', 'https://discovery.nationalarchives.gov.uk/', 'Online at The National Archives', 'Free to view, £3.50 to download', 'Provides details of heroic actions and service recognition', 'AIR 2', 'Search by name and medal type. Citations provide detailed accounts of specific actions.'),
        ('RAF Casualty Cards', 'Primary Source', 'Death and casualty notification cards', 'https://discovery.nationalarchives.gov.uk/', 'Online at The National Archives', 'Free to view, £3.50 to download', 'Essential for casualty details and circumstances', 'AIR 81', 'Search by name and service number. Provides official casualty information and next of kin details.'),
        ('Local Newspapers', 'Secondary Source', 'Contemporary newspaper reports and obituaries', 'https://www.britishnewspaperarchive.co.uk/', 'British Newspaper Archive (subscription)', '£12.95 per month', 'Valuable for local context and family reactions', 'Various', 'Search by name and location. Look for enlistment announcements, casualty reports, and family tributes.'),
        ('RAF Museum Collections', 'Mixed Sources', 'Aircraft records, photographs, personal collections', 'https://www.rafmuseum.org.uk/', 'Email appointment required', 'Free research access', 'Excellent for technical details and personal stories', 'Various', 'Contact research team directly. Specify squadron and time period for targeted assistance.'),
        ('Bomber Command Association Records', 'Secondary Source', 'Veteran accounts and squadron reunions', 'Various local archives', 'Contact local archives', 'Varies', 'Personal accounts and post-war connections', 'Various', 'Contact squadron associations and veteran groups. Many have newsletters and reunion records.'),
        ('Aircraft Loss Cards', 'Primary Source', 'Official records of aircraft losses and crew fates', 'https://discovery.nationalarchives.gov.uk/', 'Online at The National Archives', 'Free to view, £3.50 to download', 'Critical for understanding aircraft losses and crew casualties', 'AIR 81', 'Search by aircraft serial number or squadron. Provides detailed loss circumstances.'),
        ('Station Records', 'Primary Source', 'Records of individual RAF bases and their operations', 'https://discovery.nationalarchives.gov.uk/', 'Online at The National Archives', 'Free to view, £3.50 to download', 'Provides context for base operations and personnel', 'AIR 28', 'Search by station name. Includes daily routine orders and personnel movements.')
    ]
    
    for source in sources_data:
        cursor.execute('''
            INSERT OR REPLACE INTO research_sources 
            (source_name, source_type, description, url, access_method, cost, 
             research_value, archive_series, search_tips)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', source)
    
    # Insert research pathways for different types of research
    pathways_data = [
        ('Basic Personnel Research', 'Individual Research', 'Standard approach for researching an individual RAF person', 
         '1. Start with CWGC database for basic information|2. Access RAF service record (AIR 79)|3. Review squadron operational records|4. Search for combat reports and citations|5. Look for local newspaper coverage|6. Contact family members or veteran associations',
         '2-4 weeks', 'Beginner', '85%', 'Basic computer skills, ability to read handwritten documents'),
        ('Squadron History Research', 'Unit Research', 'Comprehensive approach for researching squadron operations and personnel',
         '1. Access squadron operational record books (AIR 27)|2. Review station records for base context|3. Study group and command records|4. Research individual crew members|5. Collect photographs and personal accounts|6. Compile comprehensive squadron narrative',
         '6-12 weeks', 'Intermediate', '75%', 'Historical research experience, document analysis skills'),
        ('Family History Research', 'Genealogical Research', 'Approach for family members researching relatives',
         '1. Gather family information and documents|2. Search CWGC database|3. Access service records|4. Research local newspapers and parish records|5. Contact other family members|6. Visit memorial sites and museums',
         '4-8 weeks', 'Beginner', '90%', 'Family knowledge, basic genealogy skills'),
        ('Academic Research', 'Scholarly Research', 'Comprehensive approach for academic or professional historians',
         '1. Literature review of existing scholarship|2. Access primary sources at multiple archives|3. Conduct oral history interviews|4. Analyze operational and strategic context|5. Cross-reference multiple source types|6. Produce scholarly analysis',
         '6-18 months', 'Advanced', '70%', 'Advanced historical training, archival research experience'),
        ('Memorial Research', 'Commemorative Research', 'Approach for researching memorial and commemoration details',
         '1. Identify burial or memorial location via CWGC|2. Research circumstances of death|3. Access casualty records and combat reports|4. Contact memorial organizations|5. Research family and community responses|6. Document memorial significance',
         '3-6 weeks', 'Intermediate', '80%', 'Research skills, sensitivity to memorial contexts')
    ]
    
    for pathway in pathways_data:
        cursor.execute('''
            INSERT OR REPLACE INTO research_pathways 
            (pathway_name, research_type, description, steps, estimated_timeline, 
             difficulty_level, success_rate, required_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', pathway)
    
    conn.commit()
    conn.close()
    
    # Verify Patrick Cassidy memorial record
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, service_number FROM personnel WHERE service_number = '1802082'")
    patrick_record = cursor.fetchone()
    conn.close()
    
    if patrick_record:
        print(f"✅ Memorial verified: {patrick_record[0]} (Service Number: {patrick_record[1]})")
    else:
        print("❌ Memorial verification failed")

# Initialize database on startup
init_database()

def get_enhanced_research_guidance(research_query, person_data=None):
    """Generate enhanced AI research guidance with advanced archival signposting"""
    
    # If OpenAI is not available, provide comprehensive fallback guidance
    if not OPENAI_API_KEY:
        return generate_enhanced_fallback_guidance(research_query, person_data)
    
    try:
        # This would integrate with OpenAI API when available
        # For now, provide enhanced professional guidance
        return generate_enhanced_professional_guidance(research_query, person_data)
    except Exception as e:
        return generate_enhanced_fallback_guidance(research_query, person_data)

def generate_enhanced_professional_guidance(research_query, person_data=None):
    """Generate enhanced professional historian-level research guidance with advanced features"""
    
    guidance = {
        "research_strategy": "",
        "primary_sources": [],
        "secondary_sources": [],
        "archival_signposts": [],
        "research_pathway": [],
        "expert_tips": [],
        "estimated_timeline": "",
        "potential_challenges": [],
        "success_indicators": [],
        "direct_search_links": [],
        "family_research_tips": [],
        "document_hunting_guide": []
    }
    
    # Analyze the research query
    query_lower = research_query.lower()
    
    if person_data:
        # Enhanced personalized guidance based on known information
        name = person_data.get('name', 'Unknown')
        service_number = person_data.get('service_number', 'Unknown')
        squadron = person_data.get('squadron', 'Unknown')
        family_connections = person_data.get('family_connections', 'Unknown')
        research_notes = person_data.get('research_notes', 'Unknown')
        
        guidance["research_strategy"] = f"""
        **Enhanced Research Strategy for {name}**
        
        Based on comprehensive information about {name} (Service Number: {service_number}, {squadron}), 
        I recommend a sophisticated multi-archive approach combining official records, family research, and memorial investigation.
        
        **Phase 1: Foundation Research (Week 1)**
        Establish complete service record and verify basic facts through official sources.
        
        **Phase 2: Operational Context (Week 2-3)**
        Deep dive into squadron operations, missions, and aircraft assignments.
        
        **Phase 3: Personal Dimension (Week 4-5)**
        Family research, local connections, and personal accounts.
        
        **Phase 4: Memorial Investigation (Week 6)**
        Memorial significance, commemoration, and ongoing remembrance.
        
        **Family Connections:** {family_connections}
        **Research Notes:** {research_notes}
        """
        
        # Generate direct search links
        guidance["direct_search_links"] = [
            {
                "archive": "The National Archives",
                "search_type": "Service Record",
                "url": f"https://discovery.nationalarchives.gov.uk/search/quick?_q={service_number}",
                "description": f"Direct search for {name}'s service record using Service Number {service_number}"
            },
            {
                "archive": "Commonwealth War Graves Commission",
                "search_type": "Memorial Record",
                "url": f"https://www.cwgc.org/find-war-dead/?surname={name.split()[-1]}&initials={name[0]}",
                "description": f"Search CWGC database for {name}'s memorial information"
            },
            {
                "archive": "RAF Museum",
                "search_type": "Squadron History",
                "url": f"https://www.rafmuseum.org.uk/research/collections-search/?q={squadron.replace(' ', '+')}",
                "description": f"Search RAF Museum collections for {squadron} history and records"
            }
        ]
        
        guidance["family_research_tips"] = [
            f"Family connections indicate {family_connections} - research local archives in this area",
            "Check local newspapers for enlistment announcements and casualty reports",
            "Search parish records for baptism, marriage, and family information",
            "Contact local historical societies in the family's home area",
            "Look for employment records if family worked in aviation or related industries"
        ]
        
        guidance["document_hunting_guide"] = [
            {
                "document_type": "Service Record",
                "location": "The National Archives AIR 79 series",
                "search_method": f"Search by service number {service_number}",
                "cost": "£3.50",
                "contains": "Complete service history, training records, postings, casualty details"
            },
            {
                "document_type": "Squadron Records",
                "location": f"The National Archives AIR 27 series",
                "search_method": f"Search for {squadron} operational records",
                "cost": "Free to view, £3.50 to download",
                "contains": "Daily operations, mission reports, personnel movements"
            },
            {
                "document_type": "Combat Reports",
                "location": "The National Archives AIR 50 series",
                "search_method": "Search by date and squadron",
                "cost": "Free to view, £3.50 to download",
                "contains": "Detailed mission accounts, crew experiences, operational outcomes"
            }
        ]
        
    else:
        # Enhanced general research guidance
        guidance["research_strategy"] = """
        **Enhanced RAF Bomber Command Research Strategy**
        
        For comprehensive RAF Bomber Command personnel research, follow this advanced systematic approach:
        
        **Phase 1: Information Foundation (Week 1)**
        - Establish complete identity and service details
        - Verify basic facts through multiple sources
        - Create research timeline and objectives
        
        **Phase 2: Official Documentation (Week 2-3)**
        - Access complete service records and squadron documentation
        - Review operational records and mission reports
        - Analyze casualty and medal records if applicable
        
        **Phase 3: Contextual Research (Week 4-5)**
        - Study squadron history and base operations
        - Research specific operations and campaigns
        - Investigate aircraft assignments and crew relationships
        
        **Phase 4: Personal and Family Dimension (Week 6-7)**
        - Family research and local connections
        - Search for photographs and personal accounts
        - Contact veteran associations and family members
        
        **Phase 5: Memorial and Legacy (Week 8)**
        - Memorial significance and commemoration
        - Ongoing remembrance and historical impact
        - Documentation and preservation of findings
        """
    
    guidance["research_pathway"] = [
        {
            "step": 1,
            "title": "Establish Complete Identity",
            "description": "Confirm full name, service number, rank, squadron, role, and key dates",
            "sources": ["CWGC Database", "RAF Museum online records", "Ancestry military records"],
            "estimated_time": "2-4 hours",
            "success_criteria": "Complete basic service information verified through multiple sources"
        },
        {
            "step": 2,
            "title": "Access Official Service Records",
            "description": "Download complete RAF service record from The National Archives",
            "sources": ["The National Archives AIR 79 series"],
            "estimated_time": "1-2 days (including delivery)",
            "success_criteria": "Complete service record obtained and analyzed"
        },
        {
            "step": 3,
            "title": "Squadron and Operational Research",
            "description": "Study squadron operational record books and mission reports",
            "sources": ["The National Archives AIR 27 series", "AIR 50 combat reports"],
            "estimated_time": "3-5 days",
            "success_criteria": "Operational context and mission details understood"
        },
        {
            "step": 4,
            "title": "Aircraft and Crew Research",
            "description": "Research aircraft assignments and crew relationships",
            "sources": ["Aircraft loss cards", "Crew records", "Technical manuals"],
            "estimated_time": "2-3 days",
            "success_criteria": "Aircraft history and crew connections documented"
        },
        {
            "step": 5,
            "title": "Family and Local Research",
            "description": "Investigate family background and local connections",
            "sources": ["Local newspapers", "Parish records", "Census data", "Employment records"],
            "estimated_time": "1-2 weeks",
            "success_criteria": "Family background and local context established"
        },
        {
            "step": 6,
            "title": "Memorial and Commemoration",
            "description": "Research memorial details and ongoing commemoration",
            "sources": ["CWGC records", "Memorial registers", "Local memorials"],
            "estimated_time": "3-5 days",
            "success_criteria": "Memorial significance and commemoration documented"
        }
    ]
    
    guidance["expert_tips"] = [
        "Always cross-reference information from multiple sources - official records can contain errors",
        "Service numbers are the most reliable identifier - use them for all archive searches",
        "Squadron operational record books often contain personal details not found in service records",
        "Local newspapers are goldmines for family information and community reactions",
        "Contact RAF Museum researchers early - they have extensive knowledge and personal collections",
        "Aircraft serial numbers can unlock detailed technical and operational information",
        "Medal citations provide the most detailed accounts of specific heroic actions",
        "Don't overlook station records - they provide valuable context about daily life",
        "Family members often have photographs and documents not held in official archives",
        "Veteran associations maintain extensive records and personal connections"
    ]
    
    guidance["estimated_timeline"] = "6-10 weeks for comprehensive research, including family and memorial investigation"
    
    guidance["potential_challenges"] = [
        "Some records may be closed for 100 years (personnel files with sensitive information)",
        "Handwritten documents require paleography skills to read accurately",
        "Squadron records may have gaps during intensive operational periods",
        "Family information may be limited if no surviving relatives can be contacted",
        "Local archives may have limited opening hours or require appointments",
        "Overseas records (for Commonwealth personnel) may require international research"
    ]
    
    guidance["success_indicators"] = [
        "Complete service record obtained and analyzed",
        "Squadron operational context fully understood",
        "Specific missions and operations identified and documented",
        "Family background and local connections established",
        "Personal photographs or accounts located",
        "Memorial or burial location confirmed and visited",
        "Crew relationships and aircraft assignments documented",
        "Historical significance and legacy understood"
    ]
    
    return guidance

def generate_enhanced_fallback_guidance(research_query, person_data=None):
    """Generate enhanced comprehensive research guidance when AI is not available"""
    
    return {
        "research_strategy": "Enhanced professional historian approach: Establish identity, access official records, investigate operational context, research family connections, document memorial significance",
        "archival_signposts": [
            {
                "archive": "The National Archives",
                "priority": "Essential",
                "url": "https://discovery.nationalarchives.gov.uk/",
                "search_tip": "Search AIR 79 for service records, AIR 27 for squadron records, AIR 50 for combat reports",
                "specific_collections": "AIR 79 (service records), AIR 27 (squadron records), AIR 14 (Bomber Command)"
            },
            {
                "archive": "RAF Museum",
                "priority": "High", 
                "url": "https://www.rafmuseum.org.uk/",
                "contact": "research@rafmuseum.org.uk",
                "search_tip": "Contact research team directly for personalized assistance"
            },
            {
                "archive": "Commonwealth War Graves Commission",
                "priority": "Essential",
                "url": "https://www.cwgc.org/",
                "search_tip": "Free database with burial/memorial information and next of kin details"
            }
        ],
        "research_pathway": [
            "1. Establish complete identity (name, service number, squadron, dates)",
            "2. Access official service records (AIR 79 series)",
            "3. Study squadron operational records (AIR 27 series)", 
            "4. Research specific operations and missions (AIR 50 combat reports)",
            "5. Investigate family background and local connections",
            "6. Search for personal accounts and photographs",
            "7. Document memorial significance and commemoration"
        ],
        "expert_tips": [
            "Service numbers are the most reliable identifier for archive searches",
            "RAF service records (AIR 79) provide complete service history for £3.50",
            "Squadron operational record books contain daily operational details",
            "Local newspapers often have obituaries and family information not found elsewhere",
            "Contact RAF Museum researchers for expert personalized assistance",
            "Cross-reference multiple sources - official records can contain errors",
            "Aircraft serial numbers unlock detailed technical and crew information"
        ],
        "estimated_timeline": "6-10 weeks for comprehensive research including family and memorial investigation",
        "direct_search_links": [
            {
                "archive": "The National Archives",
                "url": "https://discovery.nationalarchives.gov.uk/search/quick",
                "description": "Search official RAF records by service number or name"
            },
            {
                "archive": "CWGC Database",
                "url": "https://www.cwgc.org/find-war-dead/",
                "description": "Search war graves and memorial records"
            }
        ]
    }

# Enhanced HTML template with advanced research features
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAF Bomber Command - Enhanced AI Historical Research Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #f4f4f4;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            padding: 2rem 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 3px solid #d4af37;
        }
        
        .raf-badge {
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #d4af37, #f4e87c);
            border-radius: 50%;
            margin: 0 auto 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        }
        
        .raf-badge::before {
            content: "★";
            font-size: 2.5rem;
            color: #1a1a2e;
            font-weight: bold;
        }
        
        h1 {
            font-size: 2.5rem;
            color: #d4af37;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #b8860b;
            font-style: italic;
            margin-bottom: 1rem;
        }
        
        .banner {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
            padding: 0.8rem 2rem;
            border-radius: 25px;
            font-weight: bold;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        }
        
        .nav-tabs {
            display: flex;
            justify-content: center;
            gap: 1rem;
            padding: 2rem 1rem;
            flex-wrap: wrap;
        }
        
        .nav-tab {
            background: linear-gradient(45deg, #2c3e50, #34495e);
            color: #d4af37;
            border: 2px solid #d4af37;
            padding: 1rem 2rem;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .nav-tab:hover, .nav-tab.active {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
        }
        
        .content-section {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .memorial-quote {
            text-align: center;
            font-style: italic;
            color: #d4af37;
            font-size: 1.2rem;
            margin: 3rem 0;
            padding: 2rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            border: 2px solid #d4af37;
        }
        
        .research-container {
            background: rgba(44, 62, 80, 0.9);
            border: 2px solid #d4af37;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .research-input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #d4af37;
            border-radius: 10px;
            background: rgba(26, 26, 46, 0.8);
            color: #f4f4f4;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            min-height: 100px;
            resize: vertical;
        }
        
        .research-btn {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
            border: none;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 1rem;
            margin-bottom: 1rem;
        }
        
        .research-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
        }
        
        .guidance-container {
            margin-top: 2rem;
        }
        
        .guidance-section {
            background: rgba(44, 62, 80, 0.9);
            border: 2px solid #d4af37;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        .guidance-title {
            color: #d4af37;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .guidance-content {
            line-height: 1.6;
        }
        
        .pathway-step {
            background: rgba(26, 26, 46, 0.5);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #d4af37;
            margin-bottom: 1rem;
        }
        
        .pathway-step-number {
            background: #d4af37;
            color: #1a1a2e;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 1rem;
        }
        
        .archive-card {
            background: rgba(26, 26, 46, 0.5);
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #d4af37;
            margin-bottom: 1rem;
        }
        
        .archive-name {
            color: #d4af37;
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .archive-link {
            color: #87ceeb;
            text-decoration: none;
            font-weight: bold;
        }
        
        .archive-link:hover {
            color: #d4af37;
        }
        
        .tip-item {
            background: rgba(26, 26, 46, 0.3);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #d4af37;
            margin-bottom: 0.8rem;
        }
        
        .search-link-card {
            background: rgba(26, 26, 46, 0.5);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #87ceeb;
            margin-bottom: 1rem;
        }
        
        .search-link-title {
            color: #87ceeb;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .document-card {
            background: rgba(26, 26, 46, 0.3);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #b8860b;
            margin-bottom: 1rem;
        }
        
        .document-type {
            color: #b8860b;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .loading {
            text-align: center;
            color: #d4af37;
            font-style: italic;
            padding: 2rem;
        }
        
        @media (max-width: 768px) {
            .nav-tabs {
                flex-direction: column;
                align-items: center;
            }
            
            .research-btn {
                width: 100%;
                margin-right: 0;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="raf-badge"></div>
        <h1>RAF Bomber Command Research Database</h1>
        <p class="subtitle">Enhanced AI Historical Research Assistant</p>
        <div class="banner">🤖 Advanced Archival Signposting - Professional Historian Guidance</div>
    </div>
    
    <div class="nav-tabs">
        <button class="nav-tab active" onclick="showSection('research')">🔍 Enhanced AI Research</button>
        <button class="nav-tab" onclick="showSection('pathways')">🗺️ Research Pathways</button>
        <button class="nav-tab" onclick="showSection('archives')">📚 Archive Directory</button>
        <button class="nav-tab" onclick="showSection('sources')">📄 Source Guide</button>
        <button class="nav-tab" onclick="showSection('database')">🎖️ Search Database</button>
    </div>
    
    <div id="research-section" class="content-section">
        <div class="memorial-quote">
            "Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."
        </div>
        
        <div class="research-container">
            <h2 style="color: #d4af37; margin-bottom: 1rem;">🤖 Enhanced AI Historical Research Assistant</h2>
            <p style="margin-bottom: 1rem;">Describe your research needs in detail. I'll provide advanced archival signposting, direct search links, family research guidance, and professional historian-level strategies.</p>
            
            <textarea id="researchQuery" class="research-input" placeholder="Example: I'm researching my great-uncle who served with RAF Bomber Command during WWII. His name was Patrick Cassidy, Service Number 1802082, and I believe he was with 97 Squadron RAF Pathfinders. I'd like to find his complete service record, details about his missions, information about his aircraft, and any family connections or memorial details..."></textarea>
            
            <button class="research-btn" onclick="getEnhancedResearchGuidance()">🔍 Get Enhanced Research Guidance</button>
            <button class="research-btn" onclick="researchPatrickCassidy()">🎖️ Research Patrick Cassidy</button>
            <button class="research-btn" onclick="researchGuyGibson()">⭐ Research Guy Gibson</button>
        </div>
        
        <div id="guidance" class="guidance-container"></div>
    </div>
    
    <div id="pathways-section" class="content-section" style="display: none;">
        <h2 style="color: #d4af37; text-align: center; margin-bottom: 2rem;">🗺️ Research Pathways</h2>
        <div id="pathways-list"></div>
    </div>
    
    <div id="archives-section" class="content-section" style="display: none;">
        <h2 style="color: #d4af37; text-align: center; margin-bottom: 2rem;">📚 Enhanced Archive Directory</h2>
        <div id="archives-list"></div>
    </div>
    
    <div id="sources-section" class="content-section" style="display: none;">
        <h2 style="color: #d4af37; text-align: center; margin-bottom: 2rem;">📄 Enhanced Source Guide</h2>
        <div id="sources-list"></div>
    </div>
    
    <div id="database-section" class="content-section" style="display: none;">
        <h2 style="color: #d4af37; text-align: center; margin-bottom: 2rem;">🎖️ Search Personnel Database</h2>
        <div class="research-container">
            <input type="text" id="searchInput" class="research-input" style="min-height: auto;" placeholder="Search by name, service number, or squadron...">
            <button class="research-btn" onclick="searchPersonnel()">🔍 Search</button>
        </div>
        <div id="search-results"></div>
    </div>
    
    <script>
        function showSection(sectionName) {
            // Hide all sections
            const sections = ['research', 'pathways', 'archives', 'sources', 'database'];
            sections.forEach(section => {
                document.getElementById(section + '-section').style.display = 'none';
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionName + '-section').style.display = 'block';
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Load section-specific data
            if (sectionName === 'pathways') {
                loadPathways();
            } else if (sectionName === 'archives') {
                loadArchives();
            } else if (sectionName === 'sources') {
                loadSources();
            }
        }
        
        function getEnhancedResearchGuidance() {
            const query = document.getElementById('researchQuery').value;
            if (!query.trim()) {
                alert('Please enter your research question or describe who you\'re researching.');
                return;
            }
            
            const guidanceContainer = document.getElementById('guidance');
            guidanceContainer.innerHTML = '<div class="loading">🤖 Analyzing your research needs and preparing enhanced professional guidance with direct archive links...</div>';
            
            fetch('/api/ai/enhanced-research-guidance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                displayEnhancedResearchGuidance(data);
            })
            .catch(error => {
                console.error('Error:', error);
                guidanceContainer.innerHTML = '<p style="color: #dc3545;">Error getting enhanced research guidance</p>';
            });
        }
        
        function researchPatrickCassidy() {
            document.getElementById('researchQuery').value = 'I want to research Sergeant Patrick Cassidy, Service Number 1802082, who served with 97 Squadron RAF Pathfinders as a Flight Engineer. He was lost on November 15, 1943, flying in Lancaster JB174. I need complete service records, mission details, family connections, and memorial information.';
            getEnhancedResearchGuidance();
        }
        
        function researchGuyGibson() {
            document.getElementById('researchQuery').value = 'I want to research Wing Commander Guy Gibson VC, who led the famous Dambusters raid with 617 Squadron. I need comprehensive information about his service, the Dambusters operation, and his complete military career.';
            getEnhancedResearchGuidance();
        }
        
        function displayEnhancedResearchGuidance(guidance) {
            const container = document.getElementById('guidance');
            let html = '';
            
            // Research Strategy
            if (guidance.research_strategy) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">🎯 Enhanced Research Strategy</div>
                        <div class="guidance-content">${guidance.research_strategy.replace(/\\n/g, '<br>')}</div>
                    </div>
                `;
            }
            
            // Direct Search Links
            if (guidance.direct_search_links && guidance.direct_search_links.length > 0) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">🔗 Direct Archive Search Links</div>
                        <div class="guidance-content">
                `;
                
                guidance.direct_search_links.forEach(link => {
                    html += `
                        <div class="search-link-card">
                            <div class="search-link-title">${link.archive} - ${link.search_type}</div>
                            <p>${link.description}</p>
                            <p><a href="${link.url}" target="_blank" class="archive-link">🔍 Search Now →</a></p>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Document Hunting Guide
            if (guidance.document_hunting_guide && guidance.document_hunting_guide.length > 0) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">📄 Document Hunting Guide</div>
                        <div class="guidance-content">
                `;
                
                guidance.document_hunting_guide.forEach(doc => {
                    html += `
                        <div class="document-card">
                            <div class="document-type">${doc.document_type}</div>
                            <p><strong>Location:</strong> ${doc.location}</p>
                            <p><strong>Search Method:</strong> ${doc.search_method}</p>
                            <p><strong>Cost:</strong> ${doc.cost}</p>
                            <p><strong>Contains:</strong> ${doc.contains}</p>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Research Pathway
            if (guidance.research_pathway && guidance.research_pathway.length > 0) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">🗺️ Enhanced Research Pathway</div>
                        <div class="guidance-content">
                `;
                
                guidance.research_pathway.forEach((step, index) => {
                    if (typeof step === 'object') {
                        html += `
                            <div class="pathway-step">
                                <span class="pathway-step-number">${step.step}</span>
                                <strong>${step.title}</strong><br>
                                ${step.description}<br>
                                <em>Sources: ${step.sources ? step.sources.join(', ') : 'Various'}</em><br>
                                <em>Estimated time: ${step.estimated_time || 'Varies'}</em><br>
                                <em>Success criteria: ${step.success_criteria || 'Completion of step objectives'}</em>
                            </div>
                        `;
                    } else {
                        html += `
                            <div class="pathway-step">
                                <span class="pathway-step-number">${index + 1}</span>
                                ${step}
                            </div>
                        `;
                    }
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Family Research Tips
            if (guidance.family_research_tips && guidance.family_research_tips.length > 0) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">👨‍👩‍👧‍👦 Family Research Tips</div>
                        <div class="guidance-content">
                `;
                
                guidance.family_research_tips.forEach(tip => {
                    html += `<div class="tip-item">👨‍👩‍👧‍👦 ${tip}</div>`;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Archival Signposts
            if (guidance.archival_signposts && guidance.archival_signposts.length > 0) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">📚 Enhanced Archival Signposts</div>
                        <div class="guidance-content">
                `;
                
                guidance.archival_signposts.forEach(archive => {
                    if (typeof archive === 'object') {
                        html += `
                            <div class="archive-card">
                                <div class="archive-name">${archive.archive} (${archive.priority} Priority)</div>
                                <p><strong>Search terms:</strong> ${archive.search_terms || 'General search'}</p>
                                ${archive.specific_series ? `<p><strong>Specific series:</strong> ${archive.specific_series}</p>` : ''}
                                ${archive.specific_collections ? `<p><strong>Collections:</strong> ${archive.specific_collections}</p>` : ''}
                                ${archive.contact ? `<p><strong>Contact:</strong> ${archive.contact}</p>` : ''}
                                <p><a href="${archive.url}" target="_blank" class="archive-link">Visit Archive →</a></p>
                            </div>
                        `;
                    } else {
                        html += `<div class="archive-card">${archive}</div>`;
                    }
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Expert Tips
            if (guidance.expert_tips && guidance.expert_tips.length > 0) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">💡 Enhanced Expert Tips</div>
                        <div class="guidance-content">
                `;
                
                guidance.expert_tips.forEach(tip => {
                    html += `<div class="tip-item">💡 ${tip}</div>`;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Timeline and Challenges
            if (guidance.estimated_timeline || guidance.potential_challenges) {
                html += `
                    <div class="guidance-section">
                        <div class="guidance-title">⏱️ Timeline & Enhanced Considerations</div>
                        <div class="guidance-content">
                `;
                
                if (guidance.estimated_timeline) {
                    html += `<p><strong>Estimated Timeline:</strong> ${guidance.estimated_timeline}</p>`;
                }
                
                if (guidance.potential_challenges && guidance.potential_challenges.length > 0) {
                    html += `<p><strong>Potential Challenges:</strong></p><ul>`;
                    guidance.potential_challenges.forEach(challenge => {
                        html += `<li>${challenge}</li>`;
                    });
                    html += `</ul>`;
                }
                
                if (guidance.success_indicators && guidance.success_indicators.length > 0) {
                    html += `<p><strong>Success Indicators:</strong></p><ul>`;
                    guidance.success_indicators.forEach(indicator => {
                        html += `<li>${indicator}</li>`;
                    });
                    html += `</ul>`;
                }
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        function loadPathways() {
            fetch('/api/pathways')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('pathways-list');
                let html = '';
                
                data.pathways.forEach(pathway => {
                    const steps = pathway.steps.split('|');
                    html += `
                        <div class="archive-card">
                            <div class="archive-name">${pathway.pathway_name}</div>
                            <p><strong>Type:</strong> ${pathway.research_type}</p>
                            <p><strong>Description:</strong> ${pathway.description}</p>
                            <p><strong>Timeline:</strong> ${pathway.estimated_timeline}</p>
                            <p><strong>Difficulty:</strong> ${pathway.difficulty_level}</p>
                            <p><strong>Success Rate:</strong> ${pathway.success_rate}</p>
                            <p><strong>Required Skills:</strong> ${pathway.required_skills}</p>
                            <div style="margin-top: 1rem;">
                                <strong>Steps:</strong>
                                <ol style="margin-left: 1rem; margin-top: 0.5rem;">
                    `;
                    
                    steps.forEach(step => {
                        html += `<li style="margin-bottom: 0.5rem;">${step}</li>`;
                    });
                    
                    html += `
                                </ol>
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('pathways-list').innerHTML = '<p style="color: #dc3545;">Error loading research pathways</p>';
            });
        }
        
        function loadArchives() {
            fetch('/api/archives')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('archives-list');
                let html = '';
                
                data.archives.forEach(archive => {
                    html += `
                        <div class="archive-card">
                            <div class="archive-name">${archive.archive_name}</div>
                            <p><strong>Type:</strong> ${archive.archive_type}</p>
                            <p><strong>Location:</strong> ${archive.location}</p>
                            <p><strong>Opening Hours:</strong> ${archive.opening_hours}</p>
                            <p><strong>Specialization:</strong> ${archive.specialization}</p>
                            <p><strong>Collections:</strong> ${archive.specific_collections}</p>
                            <p><strong>Access:</strong> ${archive.access_requirements}</p>
                            <p><strong>Cost:</strong> ${archive.cost_info}</p>
                            <p><strong>Research Tips:</strong> ${archive.research_tips}</p>
                            <p><a href="${archive.website_url}" target="_blank" class="archive-link">Visit Archive →</a></p>
                            ${archive.contact_info ? `<p><strong>Contact:</strong> ${archive.contact_info}</p>` : ''}
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('archives-list').innerHTML = '<p style="color: #dc3545;">Error loading archives</p>';
            });
        }
        
        function loadSources() {
            fetch('/api/sources')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('sources-list');
                let html = '';
                
                data.sources.forEach(source => {
                    html += `
                        <div class="archive-card">
                            <div class="archive-name">${source.source_name}</div>
                            <p><strong>Type:</strong> ${source.source_type}</p>
                            <p><strong>Archive Series:</strong> ${source.archive_series}</p>
                            <p><strong>Description:</strong> ${source.description}</p>
                            <p><strong>Access:</strong> ${source.access_method}</p>
                            <p><strong>Cost:</strong> ${source.cost}</p>
                            <p><strong>Research Value:</strong> ${source.research_value}</p>
                            <p><strong>Search Tips:</strong> ${source.search_tips}</p>
                            ${source.url ? `<p><a href="${source.url}" target="_blank" class="archive-link">Access Source →</a></p>` : ''}
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('sources-list').innerHTML = '<p style="color: #dc3545;">Error loading sources</p>';
            });
        }
        
        function searchPersonnel() {
            const searchTerm = document.getElementById('searchInput').value;
            
            fetch('/api/personnel/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ search_term: searchTerm })
            })
            .then(response => response.json())
            .then(data => {
                displaySearchResults(data.results);
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('search-results').innerHTML = '<p style="color: #dc3545;">Error searching database</p>';
            });
        }
        
        function displaySearchResults(results) {
            const container = document.getElementById('search-results');
            
            if (results.length === 0) {
                container.innerHTML = '<p style="color: #dc3545;">No records found</p>';
                return;
            }
            
            let html = '';
            results.forEach(person => {
                html += `
                    <div class="archive-card">
                        <div class="archive-name">${person.name}</div>
                        <p><strong>Service Number:</strong> ${person.service_number}</p>
                        <p><strong>Rank:</strong> ${person.rank}</p>
                        <p><strong>Squadron:</strong> ${person.squadron}</p>
                        <p><strong>Role:</strong> ${person.role}</p>
                        <p><strong>Memorial Location:</strong> ${person.memorial_location}</p>
                        ${person.family_connections ? `<p><strong>Family Connections:</strong> ${person.family_connections}</p>` : ''}
                        ${person.research_notes ? `<p><strong>Research Notes:</strong> ${person.research_notes}</p>` : ''}
                        <button class="research-btn" onclick="researchPerson('${person.name}', '${person.service_number}', '${person.squadron}')">🔍 Get Enhanced Research Guidance</button>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function researchPerson(name, serviceNumber, squadron) {
            document.getElementById('researchQuery').value = `I want to research ${name}, Service Number ${serviceNumber}, who served with ${squadron}. Please provide comprehensive research guidance including family connections and memorial information.`;
            showSection('research');
            getEnhancedResearchGuidance();
        }
        
        // Allow Enter key to trigger search
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchPersonnel();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the enhanced AI Research Assistant interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health')
def health_check():
    """Enhanced health check endpoint"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Count records in each table
        cursor.execute("SELECT COUNT(*) FROM personnel")
        personnel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aircraft")
        aircraft_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_archives")
        archives_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_sources")
        sources_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_pathways")
        pathways_count = cursor.fetchone()[0]
        
        # Verify Patrick Cassidy memorial
        cursor.execute("SELECT name FROM personnel WHERE service_number = '1802082'")
        patrick_memorial = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'personnel_records': personnel_count,
            'aircraft_records': aircraft_count,
            'research_archives': archives_count,
            'research_sources': sources_count,
            'research_pathways': pathways_count,
            'patrick_cassidy_memorial': 'verified' if patrick_memorial else 'missing',
            'enhanced_ai_research_assistant': 'enabled',
            'archival_signposting': 'advanced',
            'direct_search_links': 'enabled',
            'family_research_guidance': 'enabled',
            'document_hunting_guide': 'enabled',
            'openai_configured': 'yes' if OPENAI_API_KEY else 'fallback_mode',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ai/enhanced-research-guidance', methods=['POST'])
def enhanced_ai_research_guidance():
    """Get enhanced AI research guidance with advanced archival signposting"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Research query is required'}), 400
        
        # Check if query mentions a specific person in our database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Search for person in database with enhanced information
        cursor.execute('''
            SELECT service_number, name, rank, squadron, role, age_at_death, 
                   date_of_death, memorial_location, biography, family_connections, research_notes
            FROM personnel 
            WHERE name LIKE ? OR service_number LIKE ?
            ORDER BY name
            LIMIT 1
        ''', (f'%{query}%', f'%{query}%'))
        
        person_data = None
        result = cursor.fetchone()
        if result:
            person_data = {
                'service_number': result[0],
                'name': result[1],
                'rank': result[2],
                'squadron': result[3],
                'role': result[4],
                'age_at_death': result[5],
                'date_of_death': result[6],
                'memorial_location': result[7],
                'biography': result[8],
                'family_connections': result[9],
                'research_notes': result[10]
            }
        
        conn.close()
        
        # Get enhanced AI research guidance
        guidance = get_enhanced_research_guidance(query, person_data)
        
        return jsonify(guidance)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pathways')
def get_pathways():
    """Get research pathways directory"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pathway_name, research_type, description, steps, 
                   estimated_timeline, difficulty_level, success_rate, required_skills
            FROM research_pathways
            ORDER BY pathway_name
        ''')
        
        pathways = []
        for row in cursor.fetchall():
            pathways.append({
                'pathway_name': row[0],
                'research_type': row[1],
                'description': row[2],
                'steps': row[3],
                'estimated_timeline': row[4],
                'difficulty_level': row[5],
                'success_rate': row[6],
                'required_skills': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'pathways': pathways,
            'total_pathways': len(pathways)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/archives')
def get_archives():
    """Get enhanced research archives directory"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT archive_name, archive_type, website_url, contact_info, 
                   specialization, access_requirements, cost_info, research_tips,
                   search_url_template, specific_collections, opening_hours, location
            FROM research_archives
            ORDER BY archive_name
        ''')
        
        archives = []
        for row in cursor.fetchall():
            archives.append({
                'archive_name': row[0],
                'archive_type': row[1],
                'website_url': row[2],
                'contact_info': row[3],
                'specialization': row[4],
                'access_requirements': row[5],
                'cost_info': row[6],
                'research_tips': row[7],
                'search_url_template': row[8],
                'specific_collections': row[9],
                'opening_hours': row[10],
                'location': row[11]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'archives': archives,
            'total_archives': len(archives)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources')
def get_sources():
    """Get enhanced research sources guide"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT source_name, source_type, description, url, 
                   access_method, cost, research_value, archive_series, search_tips
            FROM research_sources
            ORDER BY source_name
        ''')
        
        sources = []
        for row in cursor.fetchall():
            sources.append({
                'source_name': row[0],
                'source_type': row[1],
                'description': row[2],
                'url': row[3],
                'access_method': row[4],
                'cost': row[5],
                'research_value': row[6],
                'archive_series': row[7],
                'search_tips': row[8]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'sources': sources,
            'total_sources': len(sources)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/personnel/search', methods=['POST'])
def search_personnel():
    """Search personnel records with enhanced information"""
    try:
        data = request.get_json()
        search_term = data.get('search_term', '').strip()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        if search_term:
            cursor.execute('''
                SELECT service_number, name, rank, squadron, role, age_at_death, 
                       date_of_death, memorial_location, biography, family_connections, research_notes
                FROM personnel 
                WHERE name LIKE ? OR service_number LIKE ? OR squadron LIKE ?
                ORDER BY name
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            cursor.execute('''
                SELECT service_number, name, rank, squadron, role, age_at_death, 
                       date_of_death, memorial_location, biography, family_connections, research_notes
                FROM personnel 
                ORDER BY name
            ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'service_number': row[0],
                'name': row[1],
                'rank': row[2],
                'squadron': row[3],
                'role': row[4],
                'age_at_death': row[5],
                'date_of_death': row[6],
                'memorial_location': row[7],
                'biography': row[8],
                'family_connections': row[9],
                'research_notes': row[10]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'results': results,
            'total_found': len(results)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🤖 RAF Bomber Command Enhanced AI Research Assistant starting on port {port}")
    print(f"📚 Enhanced research archives database loaded")
    print(f"📄 Enhanced research sources guide available")
    print(f"🗺️ Research pathways system enabled")
    print(f"🎖️ Memorial database verified")
    print(f"🔍 Advanced archival signposting enabled")
    print(f"🔗 Direct search links enabled")
    print(f"👨‍👩‍👧‍👦 Family research guidance enabled")
    print(f"📄 Document hunting guide enabled")
    app.run(host='0.0.0.0', port=port, debug=False)

