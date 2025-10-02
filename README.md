# RAF Bomber Command Research Database

> **Memorial Dedication:** *"Their memory lives on - preserved in code, honored in history, accessible to all, never to be forgotten."*

A comprehensive digital memorial and research database honoring **Sergeant Patrick Cassidy** (Service Number 1802082) and all RAF Bomber Command personnel who served during World War II.

## 🎖️ Memorial Significance

This database preserves the memory of **Sergeant Patrick Cassidy**, a Flight Engineer with 97 Squadron RAF Pathfinders who was killed when Lancaster JB174 was shot down during a raid on Hanover on 8/9 October 1943. At just 20 years old, Patrick exemplified the courage and dedication of RAF Bomber Command aircrew.

## 🌐 Live Production System

**Production URL:** [https://58hpi8cw090y.manus.space](https://58hpi8cw090y.manus.space)

## ✨ Key Features

- **Personnel Database:** Search 125,012+ RAF personnel records
- **AI Research System:** Multi-agent historical analysis with 5 specialist agents
- **WCAG 2.1 AA Accessibility:** Full accessibility compliance
- **Mobile Responsive:** Professional RAF-themed design
- **Production Security:** Rate limiting and comprehensive validation

## 🚀 Quick Start

```bash
git clone https://github.com/tiarnanlarkin/raf-bomber-command-database.git
cd raf-bomber-command-database
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your-api-key-here

# Run the application
python app.py
```

## 🤖 AI Research System

The multi-agent AI research system features 5 specialist agents:

- **Personnel Specialist** - Biographical research and service records
- **Aircraft Specialist** - Technical analysis and service history  
- **Operations Specialist** - Mission analysis and tactical evaluation
- **Historical Context Specialist** - Strategic analysis and significance
- **Statistical Analyst** - Data patterns and quantitative analysis

## ♿ Accessibility Features

- **WCAG 2.1 AA Compliant** - Full accessibility compliance
- **Keyboard Navigation** - Complete keyboard support
- **Screen Reader Support** - ARIA labels and live regions
- **High Contrast Mode** - Visual accessibility support
- **Mobile Responsive** - Touch-friendly interface

## 📁 Project Structure

```
raf-bomber-command-database/
├── README.md                           # This file
├── app.py                             # Main Flask application
├── ai_system/
│   └── complete_ai_research_system.py # Multi-agent AI research
├── templates/
│   └── index.html                     # Frontend interface
├── docs/
│   └── RAF_BOMBER_COMMAND_FINAL_DEPLOYMENT_REPORT.md
└── requirements.txt                   # Python dependencies
```

## 🔧 Configuration

Create a `.env` file with:

```env
OPENAI_API_KEY=your-openai-api-key-here
FLASK_ENV=production
DATABASE_PATH=/tmp/raf_bomber_command.db
```

## 🎖️ Memorial Dedication

**Sergeant Patrick Cassidy** (Service Number 1802082)  
Flight Engineer, 97 Squadron RAF Pathfinders  
Killed in Action: 8/9 October 1943, Age 20  
Memorial: Runnymede Memorial Panel 119  

And to all **125,012+ RAF Bomber Command personnel** who served during World War II.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Created with respect and dedication to honor those who served.*

