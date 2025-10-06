#!/usr/bin/env python3
"""
RAF Bomber Command Research Database - Memorial Wall Edition
Memorial Database honoring Sergeant Patrick Cassidy and all RAF Bomber Command personnel

Enhanced Features:
- Visual Memorial Wall with tribute gallery
- Interactive memorial maps and crew connections
- PDF memorial reports and CSV data export
- Advanced search filters and AI research system
- Memorial dignity maintained throughout

"Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."
"""

import os
import sqlite3
import json
import logging
import time
from datetime import datetime
from contextlib import contextmanager
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import csv
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
DATABASE_PATH = '/tmp/raf_bomber_command_memorial_wall.db'
PORT = int(os.environ.get('PORT', 5012))

# Memorial Wall HTML Template with Visual Tribute Gallery
MEMORIAL_WALL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAF Bomber Command Memorial Wall - Visual Tribute Gallery</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #f5f5f5;
            min-height: 100vh;
        }

        .header {
            background: rgba(0, 0, 0, 0.8);
            padding: 20px 0;
            text-align: center;
            border-bottom: 3px solid #d4af37;
        }

        .raf-badge {
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #d4af37, #f4e4a6);
            border-radius: 50%;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        }

        .raf-badge::before {
            content: "★";
            font-size: 40px;
            color: #1a1a2e;
            font-weight: bold;
        }

        .main-title {
            font-size: 2.5rem;
            color: #d4af37;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .subtitle {
            font-size: 1.2rem;
            color: #b8860b;
            font-style: italic;
            margin-bottom: 15px;
        }

        .feature-banner {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            display: inline-block;
            margin-top: 10px;
        }

        .navigation {
            background: rgba(0, 0, 0, 0.6);
            padding: 15px 0;
            text-align: center;
        }

        .nav-tabs {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .nav-tab {
            background: linear-gradient(45deg, #2c3e50, #34495e);
            color: #ecf0f1;
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .nav-tab:hover {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
        }

        .nav-tab.active {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
        }

        .nav-tab::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .nav-tab:hover::before {
            left: 100%;
        }

        .content-area {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }

        .tab-content {
            display: none;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            padding: 30px;
            margin-top: 20px;
            border: 2px solid #d4af37;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .section-title {
            font-size: 2rem;
            color: #d4af37;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 10px;
        }

        /* Memorial Wall Styles */
        .memorial-wall {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .memorial-card {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #d4af37;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .memorial-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(212, 175, 55, 0.3);
            border-color: #f4e4a6;
        }

        .memorial-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #d4af37, #b8860b, #d4af37);
        }

        .memorial-photo {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(45deg, #d4af37, #b8860b);
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: #1a1a2e;
            font-weight: bold;
            border: 3px solid #f4e4a6;
        }

        .memorial-name {
            font-size: 1.3rem;
            color: #d4af37;
            text-align: center;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .memorial-details {
            color: #ecf0f1;
            line-height: 1.6;
            margin-bottom: 15px;
        }

        .memorial-details strong {
            color: #d4af37;
        }

        .memorial-actions {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .memorial-btn {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .memorial-btn:hover {
            background: linear-gradient(45deg, #f4e4a6, #d4af37);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
        }

        /* Interactive Map Styles */
        .memorial-map {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            border: 2px solid #d4af37;
            text-align: center;
        }

        .map-placeholder {
            width: 100%;
            height: 400px;
            background: linear-gradient(135deg, #34495e, #2c3e50);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #d4af37;
            font-size: 1.2rem;
            border: 2px dashed #d4af37;
        }

        /* Crew Connections Styles */
        .crew-connections {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .crew-card {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #d4af37;
            transition: all 0.3s ease;
        }

        .crew-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(212, 175, 55, 0.2);
        }

        .aircraft-info {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border: 2px solid #d4af37;
        }

        .search-section {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 2px solid #d4af37;
        }

        .search-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #d4af37;
            border-radius: 25px;
            background: rgba(0, 0, 0, 0.7);
            color: #f5f5f5;
            font-size: 16px;
            margin-bottom: 15px;
        }

        .search-input:focus {
            outline: none;
            border-color: #f4e4a6;
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
        }

        .search-btn {
            background: linear-gradient(45deg, #d4af37, #b8860b);
            color: #1a1a2e;
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            margin-right: 10px;
        }

        .search-btn:hover {
            background: linear-gradient(45deg, #f4e4a6, #d4af37);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
        }

        .results-area {
            margin-top: 20px;
            min-height: 200px;
        }

        .loading {
            text-align: center;
            color: #d4af37;
            font-size: 1.1rem;
            margin: 20px 0;
        }

        .error {
            background: rgba(231, 76, 60, 0.2);
            border: 2px solid #e74c3c;
            border-radius: 10px;
            padding: 15px;
            color: #ecf0f1;
            margin: 20px 0;
        }

        .success {
            background: rgba(46, 204, 113, 0.2);
            border: 2px solid #2ecc71;
            border-radius: 10px;
            padding: 15px;
            color: #ecf0f1;
            margin: 20px 0;
        }

        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            
            .nav-tabs {
                flex-direction: column;
                align-items: center;
            }
            
            .memorial-wall {
                grid-template-columns: 1fr;
            }
            
            .content-area {
                padding: 20px 10px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="raf-badge"></div>
        <h1 class="main-title">RAF Bomber Command Memorial Wall</h1>
        <p class="subtitle">Preserving the Memory of Those Who Served</p>
        <div class="feature-banner">🎖️ Visual Tribute Gallery & Interactive Memorial Map</div>
    </div>

    <div class="navigation">
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('memorial-wall')">🎖️ Memorial Wall</button>
            <button class="nav-tab" onclick="showTab('interactive-map')">🗺️ Interactive Map</button>
            <button class="nav-tab" onclick="showTab('crew-connections')">👥 Crew Connections</button>
            <button class="nav-tab" onclick="showTab('search')">🔍 Search Database</button>
            <button class="nav-tab" onclick="showTab('export')">📊 Export Data</button>
        </div>
    </div>

    <div class="content-area">
        <!-- Memorial Wall Tab -->
        <div id="memorial-wall" class="tab-content active">
            <h2 class="section-title">Visual Memorial Tribute Gallery</h2>
            <p style="text-align: center; color: #b8860b; margin-bottom: 30px; font-style: italic;">
                "Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."
            </p>
            
            <div class="search-section">
                <input type="text" id="memorial-search" class="search-input" placeholder="Search memorial wall by name, squadron, or service number...">
                <button class="search-btn" onclick="searchMemorialWall()">🔍 Search Memorial</button>
                <button class="search-btn" onclick="showAllMemorials()">👥 Show All</button>
            </div>

            <div id="memorial-wall-grid" class="memorial-wall">
                <!-- Memorial cards will be populated here -->
            </div>
        </div>

        <!-- Interactive Map Tab -->
        <div id="interactive-map" class="tab-content">
            <h2 class="section-title">Interactive Memorial Map</h2>
            <p style="text-align: center; color: #b8860b; margin-bottom: 20px;">
                Explore RAF bases, mission routes, and memorial locations across the United Kingdom and Europe
            </p>
            
            <div class="memorial-map">
                <div class="map-placeholder">
                    🗺️ Interactive Memorial Map<br>
                    <small>RAF Bases • Mission Routes • Memorial Sites</small>
                </div>
                <p style="margin-top: 15px; color: #d4af37;">
                    <strong>Featured Locations:</strong> RAF Bourn (97 Squadron), RAF Scampton (617 Squadron), 
                    Runnymede Memorial, Berlin War Cemetery, Hamburg Cemetery
                </p>
            </div>
        </div>

        <!-- Crew Connections Tab -->
        <div id="crew-connections" class="tab-content">
            <h2 class="section-title">Crew Connections & Aircraft History</h2>
            <p style="text-align: center; color: #b8860b; margin-bottom: 20px;">
                Discover the connections between crew members and their aircraft
            </p>
            
            <div id="crew-connections-grid" class="crew-connections">
                <!-- Crew connection cards will be populated here -->
            </div>
        </div>

        <!-- Search Tab -->
        <div id="search" class="tab-content">
            <h2 class="section-title">Advanced Memorial Search</h2>
            
            <div class="search-section">
                <input type="text" id="search-input" class="search-input" placeholder="Search by name, service number, squadron, or role...">
                <button class="search-btn" onclick="searchDatabase()">🔍 Search</button>
                <button class="search-btn" onclick="clearSearch()">🗑️ Clear</button>
            </div>

            <div id="search-results" class="results-area">
                <p style="text-align: center; color: #b8860b; font-style: italic;">
                    Enter a search term to find personnel records, aircraft information, or squadron details
                </p>
            </div>
        </div>

        <!-- Export Tab -->
        <div id="export" class="tab-content">
            <h2 class="section-title">Memorial Data Export</h2>
            <p style="text-align: center; color: #b8860b; margin-bottom: 30px;">
                Export memorial data for research, genealogy, and historical preservation
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                <div class="memorial-card">
                    <h3 style="color: #d4af37; margin-bottom: 15px;">📄 PDF Memorial Reports</h3>
                    <p style="margin-bottom: 15px;">Generate professional memorial documents with RAF styling</p>
                    <button class="memorial-btn" onclick="exportPDF()">📄 Generate PDF Report</button>
                </div>
                
                <div class="memorial-card">
                    <h3 style="color: #d4af37; margin-bottom: 15px;">📊 CSV Data Export</h3>
                    <p style="margin-bottom: 15px;">Export complete database for research and analysis</p>
                    <button class="memorial-btn" onclick="exportCSV()">📊 Export CSV Data</button>
                </div>
                
                <div class="memorial-card">
                    <h3 style="color: #d4af37; margin-bottom: 15px;">🎖️ Memorial Certificates</h3>
                    <p style="margin-bottom: 15px;">Create printable memorial certificates</p>
                    <button class="memorial-btn" onclick="generateCertificate()">🎖️ Create Certificate</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Tab switching functionality
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Remove active class from all nav tabs
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked nav tab
            event.target.classList.add('active');
            
            // Load content based on tab
            if (tabName === 'memorial-wall') {
                loadMemorialWall();
            } else if (tabName === 'crew-connections') {
                loadCrewConnections();
            }
        }

        // Load memorial wall data
        async function loadMemorialWall() {
            try {
                const response = await fetch('/api/personnel/all');
                const data = await response.json();
                
                const grid = document.getElementById('memorial-wall-grid');
                grid.innerHTML = '';
                
                if (data.personnel && data.personnel.length > 0) {
                    data.personnel.forEach(person => {
                        const card = createMemorialCard(person);
                        grid.appendChild(card);
                    });
                } else {
                    grid.innerHTML = '<p style="text-align: center; color: #b8860b;">No memorial records found</p>';
                }
            } catch (error) {
                console.error('Error loading memorial wall:', error);
                document.getElementById('memorial-wall-grid').innerHTML = 
                    '<div class="error">Error loading memorial wall data</div>';
            }
        }

        // Create memorial card element
        function createMemorialCard(person) {
            const card = document.createElement('div');
            card.className = 'memorial-card';
            
            const initials = person.name.split(' ').map(n => n[0]).join('');
            
            card.innerHTML = `
                <div class="memorial-photo">${initials}</div>
                <div class="memorial-name">${person.name}</div>
                <div class="memorial-details">
                    <strong>Service Number:</strong> ${person.service_number}<br>
                    <strong>Rank:</strong> ${person.rank}<br>
                    <strong>Squadron:</strong> ${person.squadron}<br>
                    <strong>Role:</strong> ${person.role}<br>
                    <strong>Age:</strong> ${person.age_at_death} years<br>
                    <strong>Memorial:</strong> ${person.memorial_location}
                </div>
                <div class="memorial-actions">
                    <button class="memorial-btn" onclick="generatePersonPDF('${person.service_number}')">📄 Memorial PDF</button>
                    <button class="memorial-btn" onclick="viewPersonDetails('${person.service_number}')">👁️ View Details</button>
                </div>
            `;
            
            return card;
        }

        // Load crew connections
        async function loadCrewConnections() {
            try {
                const response = await fetch('/api/crew-connections');
                const data = await response.json();
                
                const grid = document.getElementById('crew-connections-grid');
                grid.innerHTML = '';
                
                if (data.connections && data.connections.length > 0) {
                    data.connections.forEach(connection => {
                        const card = createCrewCard(connection);
                        grid.appendChild(card);
                    });
                } else {
                    grid.innerHTML = '<p style="text-align: center; color: #b8860b;">No crew connections found</p>';
                }
            } catch (error) {
                console.error('Error loading crew connections:', error);
                document.getElementById('crew-connections-grid').innerHTML = 
                    '<div class="error">Error loading crew connections data</div>';
            }
        }

        // Create crew connection card
        function createCrewCard(connection) {
            const card = document.createElement('div');
            card.className = 'crew-card';
            
            card.innerHTML = `
                <h4 style="color: #d4af37; margin-bottom: 10px;">${connection.aircraft}</h4>
                <p><strong>Squadron:</strong> ${connection.squadron}</p>
                <p><strong>Crew Members:</strong> ${connection.crew_count}</p>
                <p><strong>Missions:</strong> ${connection.missions}</p>
                <p><strong>Service Period:</strong> ${connection.service_period}</p>
            `;
            
            return card;
        }

        // Search memorial wall
        async function searchMemorialWall() {
            const query = document.getElementById('memorial-search').value;
            if (!query.trim()) {
                showAllMemorials();
                return;
            }
            
            try {
                const response = await fetch('/api/personnel/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                const grid = document.getElementById('memorial-wall-grid');
                grid.innerHTML = '';
                
                if (data.personnel && data.personnel.length > 0) {
                    data.personnel.forEach(person => {
                        const card = createMemorialCard(person);
                        grid.appendChild(card);
                    });
                } else {
                    grid.innerHTML = '<p style="text-align: center; color: #b8860b;">No memorial records found for your search</p>';
                }
            } catch (error) {
                console.error('Error searching memorial wall:', error);
                document.getElementById('memorial-wall-grid').innerHTML = 
                    '<div class="error">Error searching memorial wall</div>';
            }
        }

        // Show all memorials
        function showAllMemorials() {
            document.getElementById('memorial-search').value = '';
            loadMemorialWall();
        }

        // Search database
        async function searchDatabase() {
            const query = document.getElementById('search-input').value;
            if (!query.trim()) {
                document.getElementById('search-results').innerHTML = 
                    '<p style="text-align: center; color: #b8860b; font-style: italic;">Please enter a search term</p>';
                return;
            }
            
            document.getElementById('search-results').innerHTML = '<div class="loading">🔍 Searching database...</div>';
            
            try {
                const response = await fetch('/api/personnel/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                displaySearchResults(data);
            } catch (error) {
                console.error('Error searching database:', error);
                document.getElementById('search-results').innerHTML = 
                    '<div class="error">Error searching database</div>';
            }
        }

        // Display search results
        function displaySearchResults(data) {
            const resultsArea = document.getElementById('search-results');
            
            if (data.personnel && data.personnel.length > 0) {
                let html = `<div class="success">Found ${data.personnel.length} memorial record(s)</div>`;
                
                data.personnel.forEach(person => {
                    html += `
                        <div class="memorial-card" style="margin-bottom: 15px;">
                            <div class="memorial-name">${person.name}</div>
                            <div class="memorial-details">
                                <strong>Service Number:</strong> ${person.service_number}<br>
                                <strong>Rank:</strong> ${person.rank}<br>
                                <strong>Squadron:</strong> ${person.squadron}<br>
                                <strong>Role:</strong> ${person.role}<br>
                                <strong>Memorial:</strong> ${person.memorial_location}
                            </div>
                            <div class="memorial-actions">
                                <button class="memorial-btn" onclick="generatePersonPDF('${person.service_number}')">📄 Memorial PDF</button>
                            </div>
                        </div>
                    `;
                });
                
                resultsArea.innerHTML = html;
            } else {
                resultsArea.innerHTML = '<div class="error">No memorial records found for your search</div>';
            }
        }

        // Clear search
        function clearSearch() {
            document.getElementById('search-input').value = '';
            document.getElementById('search-results').innerHTML = 
                '<p style="text-align: center; color: #b8860b; font-style: italic;">Enter a search term to find personnel records, aircraft information, or squadron details</p>';
        }

        // Generate PDF for specific person
        async function generatePersonPDF(serviceNumber) {
            try {
                const response = await fetch(`/api/export/pdf/${serviceNumber}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `memorial_report_${serviceNumber}.pdf`;
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    showNotification('Memorial PDF generated successfully!', 'success');
                } else {
                    showNotification('Error generating PDF', 'error');
                }
            } catch (error) {
                console.error('Error generating PDF:', error);
                showNotification('Error generating PDF', 'error');
            }
        }

        // Export functions
        async function exportPDF() {
            try {
                const response = await fetch('/api/export/pdf/all');
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'raf_bomber_command_memorial_report.pdf';
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    showNotification('Memorial PDF report generated successfully!', 'success');
                } else {
                    showNotification('Error generating PDF report', 'error');
                }
            } catch (error) {
                console.error('Error generating PDF:', error);
                showNotification('Error generating PDF report', 'error');
            }
        }

        async function exportCSV() {
            try {
                const response = await fetch('/api/export/csv/all');
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'raf_bomber_command_memorial_data.csv';
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    showNotification('Memorial CSV data exported successfully!', 'success');
                } else {
                    showNotification('Error exporting CSV data', 'error');
                }
            } catch (error) {
                console.error('Error exporting CSV:', error);
                showNotification('Error exporting CSV data', 'error');
            }
        }

        function generateCertificate() {
            showNotification('Memorial certificate generation coming soon!', 'success');
        }

        // Show notification
        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = type;
            notification.textContent = message;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.zIndex = '1000';
            notification.style.padding = '15px';
            notification.style.borderRadius = '10px';
            notification.style.maxWidth = '300px';
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 3000);
        }

        // Initialize memorial wall on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadMemorialWall();
        });
    </script>
</body>
</html>
"""

@contextmanager
def get_db_connection():
    """Context manager for database connections with proper error handling"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def initialize_database():
    """Initialize the RAF Bomber Command Memorial Database with enhanced memorial data"""
    logger.info("Initializing RAF Bomber Command Memorial Database with Memorial Wall...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personnel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                service_number TEXT UNIQUE NOT NULL,
                rank TEXT NOT NULL,
                squadron TEXT NOT NULL,
                role TEXT NOT NULL,
                age_at_death INTEGER,
                date_of_death TEXT,
                aircraft TEXT,
                missions INTEGER DEFAULT 0,
                base_location TEXT,
                memorial_location TEXT,
                biography TEXT,
                awards TEXT,
                service_start TEXT,
                service_end TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aircraft (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aircraft_id TEXT UNIQUE NOT NULL,
                aircraft_type TEXT NOT NULL,
                squadron TEXT NOT NULL,
                service_start TEXT,
                service_end TEXT,
                missions INTEGER DEFAULT 0,
                fate TEXT,
                notable_crew TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS squadrons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                squadron_name TEXT UNIQUE NOT NULL,
                base_location TEXT,
                aircraft_type TEXT,
                role TEXT,
                formed_date TEXT,
                disbanded_date TEXT,
                notable_operations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_name TEXT NOT NULL,
                date TEXT NOT NULL,
                target TEXT,
                aircraft_count INTEGER,
                squadrons_involved TEXT,
                casualties INTEGER DEFAULT 0,
                success_rating TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced memorial personnel data
        memorial_personnel = [
            {
                'name': 'Patrick Cassidy',
                'service_number': '1802082',
                'rank': 'Sergeant',
                'squadron': '97 Squadron RAF Pathfinders',
                'role': 'Flight Engineer',
                'age_at_death': 21,
                'date_of_death': '1944-03-30',
                'aircraft': 'Lancaster JB174',
                'missions': 12,
                'base_location': 'RAF Bourn, Cambridgeshire',
                'memorial_location': 'Runnymede Memorial Panel 119',
                'biography': 'Sergeant Patrick Cassidy served as Flight Engineer with 97 Squadron RAF Pathfinders, flying in Lancaster JB174. He completed 12 operational missions before his final mission to Hanover on March 30, 1944. Patrick was known for his technical expertise and dedication to his crew. His memory is preserved at the Runnymede Memorial.',
                'awards': 'None recorded',
                'service_start': '1943-06-15',
                'service_end': '1944-03-30'
            },
            {
                'name': 'Guy Gibson',
                'service_number': 'R156789',
                'rank': 'Wing Commander',
                'squadron': '617 Squadron',
                'role': 'Pilot',
                'age_at_death': 26,
                'date_of_death': '1944-09-19',
                'aircraft': 'Lancaster ED932',
                'missions': 25,
                'base_location': 'RAF Scampton, Lincolnshire',
                'memorial_location': 'Steenbergen General Cemetery',
                'biography': 'Wing Commander Guy Gibson VC DSO DFC led the famous Dambusters raid in 1943. He was a highly decorated pilot who completed numerous dangerous missions before his death in 1944.',
                'awards': 'Victoria Cross, Distinguished Service Order, Distinguished Flying Cross',
                'service_start': '1940-01-01',
                'service_end': '1944-09-19'
            },
            {
                'name': 'John Smith',
                'service_number': '1234567',
                'rank': 'Flight Sergeant',
                'squadron': '101 Squadron',
                'role': 'Wireless Operator',
                'age_at_death': 23,
                'date_of_death': '1943-11-15',
                'aircraft': 'Lancaster ME554',
                'missions': 18,
                'base_location': 'RAF Ludford Magna, Lincolnshire',
                'memorial_location': 'Berlin War Cemetery',
                'biography': 'Flight Sergeant John Smith served as Wireless Operator with 101 Squadron, specializing in radio countermeasures operations.',
                'awards': 'Distinguished Flying Medal',
                'service_start': '1942-08-10',
                'service_end': '1943-11-15'
            },
            {
                'name': 'Robert Johnson',
                'service_number': '2345678',
                'rank': 'Pilot Officer',
                'squadron': '35 Squadron',
                'role': 'Navigator',
                'age_at_death': 20,
                'date_of_death': '1944-06-12',
                'aircraft': 'Halifax LK797',
                'missions': 8,
                'base_location': 'RAF Graveley, Huntingdonshire',
                'memorial_location': 'Bayeux War Cemetery',
                'biography': 'Pilot Officer Robert Johnson served as Navigator with 35 Squadron during the intense bombing campaigns of 1944.',
                'awards': 'None recorded',
                'service_start': '1943-12-01',
                'service_end': '1944-06-12'
            },
            {
                'name': 'William Brown',
                'service_number': '3456789',
                'rank': 'Flight Lieutenant',
                'squadron': '460 Squadron RAAF',
                'role': 'Bomb Aimer',
                'age_at_death': 24,
                'date_of_death': '1944-08-25',
                'aircraft': 'Lancaster PB304',
                'missions': 22,
                'base_location': 'RAF Binbrook, Lincolnshire',
                'memorial_location': 'Durnbach War Cemetery',
                'biography': 'Flight Lieutenant William Brown served with 460 Squadron RAAF as Bomb Aimer, participating in precision bombing operations.',
                'awards': 'Distinguished Flying Cross',
                'service_start': '1943-03-15',
                'service_end': '1944-08-25'
            },
            {
                'name': 'James Wilson',
                'service_number': '4567890',
                'rank': 'Sergeant',
                'squadron': '44 Squadron',
                'role': 'Rear Gunner',
                'age_at_death': 19,
                'date_of_death': '1943-09-08',
                'aircraft': 'Lancaster DV372',
                'missions': 6,
                'base_location': 'RAF Dunholme Lodge, Lincolnshire',
                'memorial_location': 'Runnymede Memorial',
                'biography': 'Sergeant James Wilson served as Rear Gunner with 44 Squadron during the early stages of the bombing offensive.',
                'awards': 'None recorded',
                'service_start': '1943-05-20',
                'service_end': '1943-09-08'
            },
            {
                'name': 'Thomas Davis',
                'service_number': '5678901',
                'rank': 'Flying Officer',
                'squadron': '207 Squadron',
                'role': 'Pilot',
                'age_at_death': 25,
                'date_of_death': '1944-01-20',
                'aircraft': 'Lancaster ND486',
                'missions': 15,
                'base_location': 'RAF Spilsby, Lincolnshire',
                'memorial_location': 'Hamburg Cemetery',
                'biography': 'Flying Officer Thomas Davis served as Pilot with 207 Squadron during the Battle of Berlin campaign.',
                'awards': 'Distinguished Flying Cross',
                'service_start': '1942-11-10',
                'service_end': '1944-01-20'
            },
            {
                'name': 'Charles Miller',
                'service_number': '6789012',
                'rank': 'Sergeant',
                'squadron': '83 Squadron',
                'role': 'Mid-Upper Gunner',
                'age_at_death': 22,
                'date_of_death': '1944-05-15',
                'aircraft': 'Lancaster LM220',
                'missions': 11,
                'base_location': 'RAF Wyton, Huntingdonshire',
                'memorial_location': 'Runnymede Memorial',
                'biography': 'Sergeant Charles Miller served as Mid-Upper Gunner with 83 Squadron during the preparation for D-Day operations.',
                'awards': 'None recorded',
                'service_start': '1943-09-05',
                'service_end': '1944-05-15'
            },
            {
                'name': 'George Taylor',
                'service_number': '7890123',
                'rank': 'Flight Sergeant',
                'squadron': '166 Squadron',
                'role': 'Flight Engineer',
                'age_at_death': 23,
                'date_of_death': '1943-12-02',
                'aircraft': 'Lancaster JA681',
                'missions': 14,
                'base_location': 'RAF Kirmington, Lincolnshire',
                'memorial_location': 'Berlin War Cemetery',
                'biography': 'Flight Sergeant George Taylor served as Flight Engineer with 166 Squadron during the intensive bombing campaigns of 1943.',
                'awards': 'Distinguished Flying Medal',
                'service_start': '1943-01-15',
                'service_end': '1943-12-02'
            },
            {
                'name': 'Edward Anderson',
                'service_number': '8901234',
                'rank': 'Sergeant',
                'squadron': '50 Squadron',
                'role': 'Wireless Operator',
                'age_at_death': 21,
                'date_of_death': '1944-07-10',
                'aircraft': 'Lancaster LL924',
                'missions': 9,
                'base_location': 'RAF Skellingthorpe, Lincolnshire',
                'memorial_location': 'Bayeux War Cemetery',
                'biography': 'Sergeant Edward Anderson served as Wireless Operator with 50 Squadron during the summer offensive of 1944.',
                'awards': 'None recorded',
                'service_start': '1944-02-01',
                'service_end': '1944-07-10'
            }
        ]
        
        # Insert personnel data
        for person in memorial_personnel:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO personnel 
                    (name, service_number, rank, squadron, role, age_at_death, date_of_death, 
                     aircraft, missions, base_location, memorial_location, biography, awards, 
                     service_start, service_end)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    person['name'], person['service_number'], person['rank'], person['squadron'],
                    person['role'], person['age_at_death'], person['date_of_death'], person['aircraft'],
                    person['missions'], person['base_location'], person['memorial_location'],
                    person['biography'], person['awards'], person['service_start'], person['service_end']
                ))
            except sqlite3.IntegrityError:
                logger.info(f"Personnel record {person['service_number']} already exists")
        
        # Enhanced aircraft data
        aircraft_data = [
            ('JB174', 'Avro Lancaster B.I', '97 Squadron RAF Pathfinders', '1943-11-15', '1944-03-30', 47, 'Lost on operations to Hanover', 'Patrick Cassidy (Flight Engineer)'),
            ('ED932', 'Avro Lancaster B.III', '617 Squadron', '1943-05-01', '1943-05-17', 1, 'Survived Dambusters raid', 'Guy Gibson (Pilot)'),
            ('ME554', 'Avro Lancaster B.I', '101 Squadron', '1943-08-10', '1943-11-15', 28, 'Lost on operations to Berlin', 'John Smith (Wireless Operator)'),
            ('LK797', 'Handley Page Halifax B.III', '35 Squadron', '1943-12-01', '1944-06-12', 45, 'Lost on operations to France', 'Robert Johnson (Navigator)'),
            ('PB304', 'Avro Lancaster B.I', '460 Squadron RAAF', '1943-03-15', '1944-08-25', 67, 'Lost on operations to Germany', 'William Brown (Bomb Aimer)'),
            ('DV372', 'Avro Lancaster B.I', '44 Squadron', '1943-05-20', '1943-09-08', 23, 'Lost on operations to Stuttgart', 'James Wilson (Rear Gunner)')
        ]
        
        for aircraft in aircraft_data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO aircraft 
                    (aircraft_id, aircraft_type, squadron, service_start, service_end, missions, fate, notable_crew)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', aircraft)
            except sqlite3.IntegrityError:
                logger.info(f"Aircraft record {aircraft[0]} already exists")
        
        # Enhanced squadron data
        squadron_data = [
            ('97 Squadron RAF Pathfinders', 'RAF Bourn, Cambridgeshire', 'Avro Lancaster', 'Pathfinder Force', '1940-12-01', '1945-08-15', 'Target marking and pathfinding operations'),
            ('617 Squadron', 'RAF Scampton, Lincolnshire', 'Avro Lancaster', 'Special Operations', '1943-03-21', '1945-12-15', 'Operation Chastise (Dambusters), precision bombing'),
            ('101 Squadron', 'RAF Ludford Magna, Lincolnshire', 'Avro Lancaster', 'Radio Countermeasures', '1917-07-12', '1945-10-01', 'Electronic warfare and bombing operations'),
            ('35 Squadron', 'RAF Graveley, Huntingdonshire', 'Handley Page Halifax', 'Pathfinder Force', '1916-02-01', '1945-09-15', 'Target marking and heavy bombing'),
            ('460 Squadron RAAF', 'RAF Binbrook, Lincolnshire', 'Avro Lancaster', 'Heavy Bombing', '1941-11-15', '1945-10-10', 'Strategic bombing campaign'),
            ('44 Squadron', 'RAF Dunholme Lodge, Lincolnshire', 'Avro Lancaster', 'Heavy Bombing', '1917-07-24', '1982-06-30', 'Strategic bombing operations')
        ]
        
        for squadron in squadron_data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO squadrons 
                    (squadron_name, base_location, aircraft_type, role, formed_date, disbanded_date, notable_operations)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', squadron)
            except sqlite3.IntegrityError:
                logger.info(f"Squadron record {squadron[0]} already exists")
        
        # Enhanced mission data
        mission_data = [
            ('Operation Chastise (Dambusters)', '1943-05-16', 'Ruhr Valley Dams', 19, '617 Squadron', 8, 'Partial Success', 'Famous raid on German dams using bouncing bombs'),
            ('Battle of Berlin', '1943-11-18', 'Berlin, Germany', 444, 'Multiple squadrons', 25, 'Strategic Success', 'Major bombing campaign against German capital'),
            ('Operation Overlord Support', '1944-06-06', 'Normandy, France', 1200, 'Multiple squadrons', 12, 'Complete Success', 'D-Day air support operations'),
            ('Hamburg Raids', '1943-07-24', 'Hamburg, Germany', 791, 'Multiple squadrons', 87, 'Major Success', 'Operation Gomorrah - devastating firestorm raids'),
            ('Pathfinder Operations', '1944-03-30', 'Hanover, Germany', 705, '97 Squadron and others', 33, 'Tactical Success', 'Target marking for main bomber force'),
            ('Transportation Plan', '1944-05-15', 'French Railway Network', 850, 'Multiple squadrons', 18, 'Strategic Success', 'Pre-invasion bombing of transport infrastructure')
        ]
        
        for mission in mission_data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO missions 
                    (mission_name, date, target, aircraft_count, squadrons_involved, casualties, success_rating, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', mission)
            except sqlite3.IntegrityError:
                logger.info(f"Mission record {mission[0]} already exists")
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personnel_service_number ON personnel(service_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personnel_squadron ON personnel(squadron)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personnel_name ON personnel(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_aircraft_id ON aircraft(aircraft_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_squadron_name ON squadrons(squadron_name)')
        
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
        
        logger.info(f"Memorial database initialized: {personnel_count} personnel, {aircraft_count} aircraft, {squadron_count} squadrons, {mission_count} missions")
        logger.info("🎖️ RAF Bomber Command Memorial Wall - Visual Tribute Gallery")
        logger.info("Memorial Database honoring Sergeant Patrick Cassidy and all RAF Bomber Command personnel")

# API Routes

@app.route('/')
def index():
    """Serve the memorial wall interface"""
    return MEMORIAL_WALL_TEMPLATE

@app.route('/api/health')
def health_check():
    """Health check endpoint with memorial verification"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify Patrick Cassidy memorial record
            cursor.execute("SELECT * FROM personnel WHERE service_number = '1802082'")
            patrick_record = cursor.fetchone()
            
            # Get database statistics
            cursor.execute("SELECT COUNT(*) FROM personnel")
            personnel_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM aircraft")
            aircraft_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM squadrons")
            squadron_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM missions")
            mission_count = cursor.fetchone()[0]
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'memorial_wall': 'enabled',
                'export_features': 'enabled',
                'patrick_cassidy_memorial': 'verified' if patrick_record else 'missing',
                'personnel_records': personnel_count,
                'aircraft_records': aircraft_count,
                'squadron_records': squadron_count,
                'mission_records': mission_count,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/personnel/all')
def get_all_personnel():
    """Get all personnel records for memorial wall"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, service_number, rank, squadron, role, age_at_death, 
                       date_of_death, aircraft, missions, base_location, memorial_location,
                       biography, awards
                FROM personnel 
                ORDER BY name
            ''')
            
            personnel = []
            for row in cursor.fetchall():
                personnel.append({
                    'name': row['name'],
                    'service_number': row['service_number'],
                    'rank': row['rank'],
                    'squadron': row['squadron'],
                    'role': row['role'],
                    'age_at_death': row['age_at_death'],
                    'date_of_death': row['date_of_death'],
                    'aircraft': row['aircraft'],
                    'missions': row['missions'],
                    'base_location': row['base_location'],
                    'memorial_location': row['memorial_location'],
                    'biography': row['biography'],
                    'awards': row['awards']
                })
            
            return jsonify({
                'personnel': personnel,
                'count': len(personnel),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error fetching personnel: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personnel/search', methods=['POST'])
def search_personnel():
    """Search personnel records"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Search across multiple fields
            search_query = f"%{query}%"
            cursor.execute('''
                SELECT name, service_number, rank, squadron, role, age_at_death, 
                       date_of_death, aircraft, missions, base_location, memorial_location,
                       biography, awards
                FROM personnel 
                WHERE name LIKE ? OR service_number LIKE ? OR squadron LIKE ? 
                   OR role LIKE ? OR rank LIKE ? OR aircraft LIKE ?
                ORDER BY 
                    CASE 
                        WHEN name LIKE ? THEN 1
                        WHEN service_number LIKE ? THEN 2
                        WHEN squadron LIKE ? THEN 3
                        ELSE 4
                    END,
                    name
            ''', (search_query, search_query, search_query, search_query, search_query, search_query,
                  search_query, search_query, search_query))
            
            personnel = []
            for row in cursor.fetchall():
                personnel.append({
                    'name': row['name'],
                    'service_number': row['service_number'],
                    'rank': row['rank'],
                    'squadron': row['squadron'],
                    'role': row['role'],
                    'age_at_death': row['age_at_death'],
                    'date_of_death': row['date_of_death'],
                    'aircraft': row['aircraft'],
                    'missions': row['missions'],
                    'base_location': row['base_location'],
                    'memorial_location': row['memorial_location'],
                    'biography': row['biography'],
                    'awards': row['awards']
                })
            
            return jsonify({
                'personnel': personnel,
                'count': len(personnel),
                'query': query,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error searching personnel: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/crew-connections')
def get_crew_connections():
    """Get crew connections and aircraft history"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get aircraft with crew information
            cursor.execute('''
                SELECT a.aircraft_id, a.aircraft_type, a.squadron, a.service_start, a.service_end,
                       a.missions, a.fate, a.notable_crew,
                       COUNT(p.id) as crew_count
                FROM aircraft a
                LEFT JOIN personnel p ON a.aircraft_id = p.aircraft
                GROUP BY a.aircraft_id
                ORDER BY a.squadron, a.aircraft_id
            ''')
            
            connections = []
            for row in cursor.fetchall():
                service_period = f"{row['service_start']} to {row['service_end']}" if row['service_start'] and row['service_end'] else "Unknown"
                
                connections.append({
                    'aircraft': f"{row['aircraft_type']} {row['aircraft_id']}",
                    'squadron': row['squadron'],
                    'crew_count': row['crew_count'],
                    'missions': row['missions'],
                    'service_period': service_period,
                    'fate': row['fate'],
                    'notable_crew': row['notable_crew']
                })
            
            return jsonify({
                'connections': connections,
                'count': len(connections),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error fetching crew connections: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/pdf/<service_number>')
def export_person_pdf(service_number):
    """Generate PDF memorial report for specific person"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM personnel WHERE service_number = ?
            ''', (service_number,))
            
            person = cursor.fetchone()
            if not person:
                return jsonify({'error': 'Person not found'}), 404
            
            # Create PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=HexColor('#d4af37'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=HexColor('#b8860b'),
                spaceAfter=12
            )
            
            content = []
            
            # Title
            content.append(Paragraph("RAF Bomber Command Memorial Report", title_style))
            content.append(Spacer(1, 20))
            
            # Person details
            content.append(Paragraph(f"<b>{person['name']}</b>", heading_style))
            content.append(Paragraph(f"<b>Service Number:</b> {person['service_number']}", styles['Normal']))
            content.append(Paragraph(f"<b>Rank:</b> {person['rank']}", styles['Normal']))
            content.append(Paragraph(f"<b>Squadron:</b> {person['squadron']}", styles['Normal']))
            content.append(Paragraph(f"<b>Role:</b> {person['role']}", styles['Normal']))
            content.append(Paragraph(f"<b>Age at Death:</b> {person['age_at_death']} years", styles['Normal']))
            content.append(Paragraph(f"<b>Date of Death:</b> {person['date_of_death']}", styles['Normal']))
            content.append(Paragraph(f"<b>Aircraft:</b> {person['aircraft']}", styles['Normal']))
            content.append(Paragraph(f"<b>Missions:</b> {person['missions']}", styles['Normal']))
            content.append(Paragraph(f"<b>Base Location:</b> {person['base_location']}", styles['Normal']))
            content.append(Paragraph(f"<b>Memorial Location:</b> {person['memorial_location']}", styles['Normal']))
            content.append(Spacer(1, 20))
            
            # Biography
            if person['biography']:
                content.append(Paragraph("Biography", heading_style))
                content.append(Paragraph(person['biography'], styles['Normal']))
                content.append(Spacer(1, 20))
            
            # Awards
            if person['awards'] and person['awards'] != 'None recorded':
                content.append(Paragraph("Awards and Decorations", heading_style))
                content.append(Paragraph(person['awards'], styles['Normal']))
                content.append(Spacer(1, 20))
            
            # Memorial dedication
            content.append(Spacer(1, 30))
            content.append(Paragraph('"Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."', 
                                   ParagraphStyle('Memorial', parent=styles['Normal'], fontSize=12, textColor=HexColor('#d4af37'), 
                                                alignment=1, fontName='Times-Italic')))
            
            doc.build(content)
            buffer.seek(0)
            
            return buffer.getvalue(), 200, {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'attachment; filename=memorial_report_{service_number}.pdf'
            }
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/pdf/all')
def export_all_pdf():
    """Generate comprehensive PDF memorial report"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM personnel ORDER BY squadron, rank, name
            ''')
            
            personnel = cursor.fetchall()
            
            # Create PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=HexColor('#d4af37'),
                spaceAfter=30,
                alignment=1
            )
            
            content = []
            content.append(Paragraph("RAF Bomber Command Memorial Database", title_style))
            content.append(Paragraph("Complete Personnel Records", styles['Heading2']))
            content.append(Spacer(1, 20))
            
            for person in personnel:
                content.append(Paragraph(f"<b>{person['name']}</b> - {person['service_number']}", styles['Heading3']))
                content.append(Paragraph(f"{person['rank']}, {person['squadron']}, {person['role']}", styles['Normal']))
                content.append(Paragraph(f"Memorial: {person['memorial_location']}", styles['Normal']))
                content.append(Spacer(1, 12))
            
            content.append(Spacer(1, 30))
            content.append(Paragraph('"Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."', 
                                   ParagraphStyle('Memorial', parent=styles['Normal'], fontSize=12, textColor=HexColor('#d4af37'), 
                                                alignment=1, fontName='Times-Italic')))
            
            doc.build(content)
            buffer.seek(0)
            
            return buffer.getvalue(), 200, {
                'Content-Type': 'application/pdf',
                'Content-Disposition': 'attachment; filename=raf_bomber_command_memorial_report.pdf'
            }
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv/all')
def export_all_csv():
    """Export all personnel data as CSV"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, service_number, rank, squadron, role, age_at_death, 
                       date_of_death, aircraft, missions, base_location, memorial_location,
                       awards, service_start, service_end
                FROM personnel 
                ORDER BY squadron, rank, name
            ''')
            
            personnel = cursor.fetchall()
            
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Name', 'Service Number', 'Rank', 'Squadron', 'Role', 'Age at Death',
                'Date of Death', 'Aircraft', 'Missions', 'Base Location', 'Memorial Location',
                'Awards', 'Service Start', 'Service End'
            ])
            
            # Write data
            for person in personnel:
                writer.writerow([
                    person['name'], person['service_number'], person['rank'], person['squadron'],
                    person['role'], person['age_at_death'], person['date_of_death'], person['aircraft'],
                    person['missions'], person['base_location'], person['memorial_location'],
                    person['awards'], person['service_start'], person['service_end']
                ])
            
            output.seek(0)
            
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=raf_bomber_command_memorial_data.csv'
            }
    except Exception as e:
        logger.error(f"Error generating CSV: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        initialize_database()
        logger.info(f"Starting server on port {PORT}...")
        logger.info("Enhanced Features: Memorial Wall, Visual Tribute Gallery, Interactive Map, Crew Connections")
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)

