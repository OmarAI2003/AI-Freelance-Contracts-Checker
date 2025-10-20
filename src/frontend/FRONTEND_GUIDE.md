# Freelancer Legal Assistant - Frontend

Modern, responsive web interface for the Freelancer Legal Assistant AI system.

## Features

### 🎨 Beautiful UI
- Modern gradient design
- Smooth animations
- Responsive layout
- Agent-specific color themes

### 🤖 Smart Orchestration
- Automatic intent classification
- Intelligent agent routing
- A2A (Agent-to-Agent) communication
- Unified memory across agents

### 💬 Chat Interface
- Real-time messaging
- Typing indicators
- Agent switching notifications
- Quick action buttons
- File upload support

### 🔧 Agent Support
- ✅ **Action Agent** - Deployed and working
- ⏳ **Analysis Agent** - Dummy response (awaiting Dev 1)
- ⏳ **Explanation Agent** - Dummy response (awaiting Dev 2)
- ⏳ **Negotiation Agent** - Dummy response (awaiting Dev 3)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py

# Open browser
# Navigate to: http://localhost:5000
```

## Architecture

```
User → Beautiful UI → Orchestrator → Intent Classification → Agent Router
                                           ↓ ↓ ↓ ↓
                                     Analysis Explanation Negotiation Action
                                     (Dummy)  (Dummy)     (Dummy)     (Real✅)
```

See full documentation in the file for details on API, testing, and deployment.
