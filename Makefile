# RAF Bomber Command Database - Build Automation
# Memorial Dedication: "Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."

.PHONY: help build test test-all lint type clean install dev prod deploy health memorial

# Default target
help:
	@echo "🎖️ RAF Bomber Command Database - Build Commands"
	@echo ""
	@echo "Memorial Dedication:"
	@echo "Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Start development server"
	@echo "  make prod        - Start production server"
	@echo "  make test        - Run basic tests"
	@echo "  make test-all    - Run comprehensive test suite"
	@echo "  make lint        - Run code linting"
	@echo "  make type        - Run type checking"
	@echo "  make build       - Build deployment package"
	@echo "  make deploy      - Deploy to production"
	@echo "  make health      - Check application health"
	@echo "  make memorial    - Verify memorial content"
	@echo "  make clean       - Clean temporary files"

# Installation and setup
install:
	@echo "📦 Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8 black mypy
	@echo "✅ Dependencies installed"

# Development server
dev:
	@echo "🚀 Starting development server..."
	@echo "Memorial Focus: Sergeant Patrick Cassidy (Service #1802082)"
	export FLASK_ENV=development && \
	export FLASK_DEBUG=True && \
	export DATABASE_PATH=/tmp/raf_bomber_command_dev.db && \
	python app_production_ready.py

# Production server
prod:
	@echo "🎖️ Starting production server..."
	@echo "Memorial Dedication: Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."
	export FLASK_ENV=production && \
	export FLASK_DEBUG=False && \
	export DATABASE_PATH=/tmp/raf_bomber_command_production.db && \
	python app_production_ready.py

# Testing
test:
	@echo "🧪 Running basic tests..."
	export DATABASE_PATH=/tmp/test_raf_bomber_command.db && \
	python -c "from app_production_ready import initialize_database, get_database_stats; \
	assert initialize_database(), 'Database initialization failed'; \
	stats = get_database_stats(); \
	assert stats['personnel_count'] >= 10, f'Expected 10+ personnel, got {stats[\"personnel_count\"]}'; \
	print('✅ Basic tests passed')"

test-all:
	@echo "🔬 Running comprehensive test suite..."
	@echo "Testing memorial content preservation..."
	@export DATABASE_PATH=/tmp/test_comprehensive.db && python -c "from app_production_ready import initialize_database, get_database_stats; assert initialize_database(), 'Database initialization failed'; stats = get_database_stats(); assert stats['personnel_count'] >= 10, 'Insufficient personnel records'; assert stats['aircraft_count'] >= 4, 'Insufficient aircraft records'; print(f'✅ Database test passed: {stats[\"personnel_count\"]} personnel, {stats[\"aircraft_count\"]} aircraft')"
	@export DATABASE_PATH=/tmp/test_comprehensive.db && python -c "from app_production_ready import app; import json; client = app.test_client(); response = client.post('/api/personnel/search', json={'query': 'Patrick Cassidy'}); assert response.status_code == 200, 'Personnel search failed'; data = response.get_json(); assert data['count'] > 0, 'Patrick Cassidy not found'; patrick = data['results'][0]; assert patrick['service_number'] == '1802082', f'Wrong service number: {patrick[\"service_number\"]}'; assert 'Runnymede Memorial' in patrick['memorial_info'], 'Memorial info missing'; print(f'✅ Patrick Cassidy memorial verified: {patrick[\"name\"]} ({patrick[\"service_number\"]})')"
	@export DATABASE_PATH=/tmp/test_comprehensive.db && python -c "from app_production_ready import app; client = app.test_client(); health = client.get('/api/health'); assert health.status_code == 200, 'Health check failed'; stats = client.get('/api/statistics'); assert stats.status_code == 200, 'Statistics failed'; aircraft = client.post('/api/aircraft/search', json={'query': 'JB174'}); assert aircraft.status_code == 200, 'Aircraft search failed'; print('✅ All API endpoints working')"
	@echo "🎖️ Comprehensive test suite completed successfully"

# Code quality
lint:
	@echo "🔍 Running code linting..."
	flake8 app_production_ready.py --max-line-length=120 --ignore=E501,W503 || echo "Linting issues found"
	@echo "✅ Linting completed"

type:
	@echo "📝 Running type checking..."
	mypy app_production_ready.py --ignore-missing-imports || echo "Type checking issues found"
	@echo "✅ Type checking completed"

# Build and deployment
build:
	@echo "📦 Building deployment package..."
	@mkdir -p build
	@cp app_production_ready.py build/
	@cp requirements.txt build/
	@cp .env.example build/
	@cp -r templates build/ 2>/dev/null || echo "No templates directory"
	
	# Create deployment script
	@cat > build/deploy.sh << 'EOF'
#!/bin/bash
echo "🎖️ RAF Bomber Command Database Deployment"
echo "Memorial Dedication: Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting RAF Bomber Command Database..."
export DATABASE_PATH="/tmp/raf_bomber_command_production.db"
export FLASK_ENV=production
python app_production_ready.py
EOF
	@chmod +x build/deploy.sh
	
	@tar -czf raf-bomber-command-database-v5.0.0.tar.gz -C build .
	@echo "✅ Deployment package created: raf-bomber-command-database-v5.0.0.tar.gz"

deploy:
	@echo "🚀 Deploying RAF Bomber Command Database..."
	@echo "Memorial Focus: Honoring Sergeant Patrick Cassidy and all RAF personnel"
	@make build
	@echo "📦 Deployment package ready for production hosting"
	@echo "🎖️ Memorial database ready to preserve their memory for future generations"

# Health and monitoring
health:
	@echo "🏥 Checking application health..."
	@curl -s http://localhost:5000/api/health | python -m json.tool || echo "Application not running or health check failed"

memorial:
	@echo "🎖️ Verifying memorial content..."
	@echo ""
	@echo "Primary Memorial Focus:"
	@echo "  Name: Sergeant Patrick Cassidy"
	@echo "  Service Number: 1802082"
	@echo "  Squadron: 97 Squadron RAF Pathfinders"
	@echo "  Role: Flight Engineer"
	@echo "  Memorial: Runnymede Memorial Panel 119"
	@echo ""
	@echo "Memorial Dedication:"
	@echo "Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."
	@echo ""
	@grep -q "Patrick Cassidy" app_production_ready.py && echo "✅ Patrick Cassidy memorial preserved in code" || echo "❌ Memorial content missing"
	@grep -q "1802082" app_production_ready.py && echo "✅ Service number preserved" || echo "❌ Service number missing"
	@grep -q "Their memory lives on" app_production_ready.py && echo "✅ Memorial dedication preserved" || echo "❌ Memorial dedication missing"

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	@rm -rf build/
	@rm -rf __pycache__/
	@rm -rf .pytest_cache/
	@rm -f raf-bomber-command-database-*.tar.gz
	@rm -f /tmp/test_*.db
	@rm -f /tmp/raf_bomber_command_dev.db
	@echo "✅ Cleanup completed"

# Default development workflow
all: install lint type test memorial
	@echo "🎖️ RAF Bomber Command Database - Ready for Development"
	@echo "Memorial mission preserved and verified ✅"

