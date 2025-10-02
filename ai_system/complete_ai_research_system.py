#!/usr/bin/env python3
"""
RAF Bomber Command Research Database - Multi-Agent AI Research System

A sophisticated AI research system with 5 specialist agents for comprehensive
historical analysis of RAF Bomber Command personnel and operations.

Memorial Dedication: "Their memory lives on - preserved in code, honored in history, 
accessible to all, never to be forgotten."

Author: Manus AI
Version: 4.0.0
"""

import os
import json
import time
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

# Configure OpenAI - API key must be set as environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

@dataclass
class ResearchQuery:
    """Structured research query with metadata"""
    query: str
    context: str = ""
    priority: str = "normal"
    memorial_focus: bool = True

@dataclass
class AgentResponse:
    """Response from a specialist agent"""
    agent_name: str
    analysis: str
    confidence: float
    sources: List[str]
    processing_time: float

@dataclass
class ResearchResult:
    """Complete research result from multi-agent system"""
    query: str
    agents_used: List[str]
    primary_analysis: str
    supporting_evidence: List[str]
    confidence_score: float
    total_processing_time: float
    memorial_context: str

class SpecialistAgent:
    """Base class for specialist research agents"""
    
    def __init__(self, name: str, expertise: str, model: str = "gpt-4o-mini"):
        self.name = name
        self.expertise = expertise
        self.model = model
        self.client = openai.OpenAI() if openai.api_key else None
    
    def analyze(self, query: str, context: str = "") -> AgentResponse:
        """Perform specialized analysis based on agent expertise"""
        start_time = time.time()
        
        if not self.client:
            # Fallback response when OpenAI is not available
            analysis = f"AI analysis temporarily unavailable. {self.expertise} specialist would analyze: {query}"
            confidence = 0.5
        else:
            try:
                system_prompt = self._get_system_prompt()
                user_prompt = self._format_query(query, context)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                analysis = response.choices[0].message.content
                confidence = min(0.9, len(analysis) / 1000)  # Simple confidence scoring
                
            except Exception as e:
                analysis = f"Analysis error: {str(e)}. {self.expertise} specialist attempted to analyze: {query}"
                confidence = 0.3
        
        processing_time = time.time() - start_time
        
        return AgentResponse(
            agent_name=self.name,
            analysis=analysis,
            confidence=confidence,
            sources=[],
            processing_time=processing_time
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this specialist agent"""
        return f"""You are a {self.name} specializing in {self.expertise} for RAF Bomber Command research.

Your role is to provide detailed, historically accurate analysis while maintaining the respectful tone appropriate for a memorial database. Focus on factual information, historical context, and the human stories behind the data.

Always remember this is a memorial to those who served and sacrificed their lives. Maintain dignity and respect in all responses."""
    
    def _format_query(self, query: str, context: str = "") -> str:
        """Format the query for this specialist agent"""
        formatted = f"Research Query: {query}\n\n"
        if context:
            formatted += f"Additional Context: {context}\n\n"
        formatted += f"Please provide your analysis as a {self.expertise} specialist, focusing on your area of expertise."
        return formatted

class PersonnelSpecialist(SpecialistAgent):
    """Specialist in biographical research and service records"""
    
    def __init__(self):
        super().__init__(
            name="Personnel Specialist",
            expertise="biographical research, service records, and personal histories of RAF personnel"
        )

class AircraftSpecialist(SpecialistAgent):
    """Specialist in aircraft technical analysis and service history"""
    
    def __init__(self):
        super().__init__(
            name="Aircraft Specialist", 
            expertise="aircraft technical specifications, service history, and operational capabilities"
        )

class OperationsSpecialist(SpecialistAgent):
    """Specialist in mission analysis and tactical evaluation"""
    
    def __init__(self):
        super().__init__(
            name="Operations Specialist",
            expertise="mission analysis, tactical operations, and combat effectiveness"
        )

class HistoricalContextSpecialist(SpecialistAgent):
    """Specialist in strategic analysis and historical significance"""
    
    def __init__(self):
        super().__init__(
            name="Historical Context Specialist",
            expertise="strategic analysis, historical significance, and broader wartime context"
        )

class StatisticalAnalyst(SpecialistAgent):
    """Specialist in data patterns and quantitative analysis"""
    
    def __init__(self):
        super().__init__(
            name="Statistical Analyst",
            expertise="data analysis, statistical patterns, and quantitative research"
        )

class MultiAgentResearchSystem:
    """Coordinated multi-agent research system"""
    
    def __init__(self):
        self.agents = {
            'personnel': PersonnelSpecialist(),
            'aircraft': AircraftSpecialist(), 
            'operations': OperationsSpecialist(),
            'historical': HistoricalContextSpecialist(),
            'statistical': StatisticalAnalyst()
        }
        self.database_path = '/tmp/raf_bomber_command.db'
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the RAF personnel database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Create personnel table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personnel (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    service_number TEXT UNIQUE,
                    rank TEXT,
                    role TEXT,
                    squadron TEXT,
                    age_at_death INTEGER,
                    biography TEXT,
                    memorial_info TEXT
                )
            ''')
            
            # Create aircraft table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aircraft (
                    id INTEGER PRIMARY KEY,
                    serial_number TEXT UNIQUE,
                    aircraft_type TEXT,
                    squadron TEXT,
                    service_history TEXT,
                    notable_crew TEXT
                )
            ''')
            
            # Insert Patrick Cassidy record
            cursor.execute('''
                INSERT OR REPLACE INTO personnel 
                (name, service_number, rank, role, squadron, age_at_death, biography, memorial_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Patrick Cassidy',
                '1802082',
                'Sergeant',
                'Flight Engineer',
                '97 Squadron RAF Pathfinders',
                20,
                'Flight Engineer with 97 Squadron RAF Pathfinders. Patrick served with the elite Pathfinder Force, responsible for target marking and leading bomber formations to their targets. He was killed when Lancaster JB174 was shot down by German night fighters during a raid on Hanover on 8/9 October 1943. Only 20 years old at the time of his death, Patrick exemplified the courage and dedication of RAF Bomber Command aircrew.',
                'Runnymede Memorial Panel 119'
            ))
            
            # Insert Lancaster JB174 record
            cursor.execute('''
                INSERT OR REPLACE INTO aircraft
                (serial_number, aircraft_type, squadron, service_history, notable_crew)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'JB174',
                'Lancaster',
                '97 Squadron',
                'Served with 97 Squadron RAF Pathfinders. Shot down during raid on Hanover 8/9 October 1943.',
                'Sergeant Patrick Cassidy (Flight Engineer)'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def research(self, query: ResearchQuery) -> ResearchResult:
        """Conduct multi-agent research on the query"""
        start_time = time.time()
        
        # Determine which agents to use based on query content
        agents_to_use = self._select_agents(query.query)
        
        # Get database context
        db_context = self._get_database_context(query.query)
        
        # Collect responses from selected agents
        agent_responses = []
        for agent_key in agents_to_use:
            if agent_key in self.agents:
                response = self.agents[agent_key].analyze(query.query, db_context)
                agent_responses.append(response)
        
        # Synthesize results
        result = self._synthesize_results(query, agent_responses, start_time)
        
        return result
    
    def _select_agents(self, query: str) -> List[str]:
        """Select appropriate agents based on query content"""
        query_lower = query.lower()
        agents = []
        
        # Always include personnel specialist for memorial queries
        if any(term in query_lower for term in ['patrick', 'cassidy', 'personnel', 'crew', 'service']):
            agents.append('personnel')
        
        if any(term in query_lower for term in ['aircraft', 'lancaster', 'jb174', 'bomber']):
            agents.append('aircraft')
        
        if any(term in query_lower for term in ['mission', 'operation', 'raid', 'combat', 'pathfinder']):
            agents.append('operations')
        
        if any(term in query_lower for term in ['history', 'context', 'war', 'strategic']):
            agents.append('historical')
        
        if any(term in query_lower for term in ['statistics', 'data', 'analysis', 'numbers']):
            agents.append('statistical')
        
        # Default to personnel and historical if no specific matches
        if not agents:
            agents = ['personnel', 'historical']
        
        return agents
    
    def _get_database_context(self, query: str) -> str:
        """Get relevant database context for the query"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            context = "Database Context:\n"
            
            # Search personnel records
            cursor.execute('''
                SELECT name, service_number, rank, role, squadron, biography 
                FROM personnel 
                WHERE name LIKE ? OR service_number LIKE ? OR biography LIKE ?
                LIMIT 3
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            personnel_results = cursor.fetchall()
            if personnel_results:
                context += "\nPersonnel Records:\n"
                for record in personnel_results:
                    context += f"- {record[0]} ({record[1]}): {record[2]} {record[3]}, {record[4]}\n"
            
            # Search aircraft records
            cursor.execute('''
                SELECT serial_number, aircraft_type, squadron, service_history
                FROM aircraft
                WHERE serial_number LIKE ? OR service_history LIKE ?
                LIMIT 3
            ''', (f'%{query}%', f'%{query}%'))
            
            aircraft_results = cursor.fetchall()
            if aircraft_results:
                context += "\nAircraft Records:\n"
                for record in aircraft_results:
                    context += f"- {record[0]} ({record[1]}): {record[2]} - {record[3]}\n"
            
            conn.close()
            return context
            
        except Exception as e:
            return f"Database context unavailable: {e}"
    
    def _synthesize_results(self, query: ResearchQuery, responses: List[AgentResponse], start_time: float) -> ResearchResult:
        """Synthesize responses from multiple agents into a coherent result"""
        
        if not responses:
            return ResearchResult(
                query=query.query,
                agents_used=[],
                primary_analysis="No analysis available - please check system configuration.",
                supporting_evidence=[],
                confidence_score=0.0,
                total_processing_time=time.time() - start_time,
                memorial_context="This system honors the memory of RAF Bomber Command personnel."
            )
        
        # Combine analyses
        primary_analysis = responses[0].analysis
        supporting_evidence = [r.analysis for r in responses[1:]]
        
        # Calculate overall confidence
        confidence_score = sum(r.confidence for r in responses) / len(responses)
        
        # Memorial context
        memorial_context = "This research honors the memory of those who served with RAF Bomber Command during World War II."
        
        return ResearchResult(
            query=query.query,
            agents_used=[r.agent_name for r in responses],
            primary_analysis=primary_analysis,
            supporting_evidence=supporting_evidence,
            confidence_score=confidence_score,
            total_processing_time=time.time() - start_time,
            memorial_context=memorial_context
        )

# Flask application for API access
app = Flask(__name__)
CORS(app)

research_system = MultiAgentResearchSystem()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'system': 'RAF Bomber Command Multi-Agent Research System',
        'version': '4.0.0',
        'agents_available': len(research_system.agents),
        'openai_configured': openai.api_key is not None,
        'memorial_dedication': 'Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten.'
    })

@app.route('/api/multi-agent-research', methods=['POST'])
def multi_agent_research():
    """Multi-agent research endpoint"""
    try:
        data = request.get_json()
        query_text = data.get('query', '')
        
        if not query_text:
            return jsonify({'error': 'Query is required'}), 400
        
        # Create research query
        query = ResearchQuery(
            query=query_text,
            context=data.get('context', ''),
            priority=data.get('priority', 'normal'),
            memorial_focus=data.get('memorial_focus', True)
        )
        
        # Conduct research
        result = research_system.research(query)
        
        # Format response
        response = {
            'query': result.query,
            'agents_used': result.agents_used,
            'analysis': result.primary_analysis,
            'supporting_evidence': result.supporting_evidence,
            'confidence_score': result.confidence_score,
            'processing_time': result.total_processing_time,
            'memorial_context': result.memorial_context,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': 'Research system error',
            'message': str(e),
            'fallback_response': 'The multi-agent research system is temporarily unavailable. This memorial database continues to honor the memory of RAF Bomber Command personnel.'
        }), 500

if __name__ == '__main__':
    print("🎖️ RAF Bomber Command Multi-Agent Research System v4.0.0")
    print("Memorial Dedication: Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten.")
    print(f"OpenAI API Key: {'✅ Configured' if openai.api_key else '❌ Not configured - set OPENAI_API_KEY environment variable'}")
    print("Starting system on port 5002...")
    
    app.run(host='0.0.0.0', port=5002, debug=False)

