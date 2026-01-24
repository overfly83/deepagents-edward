# DeepAgents AI Platform

This is a general-purpose AI agent platform based on FastAPI and React, providing conversational AI services for various scenarios.

## Features

- 🤖 General-purpose AI agent platform
- 💬 Conversational interface
- 🔄 Streaming responses with natural typing effect
- 📱 Responsive design
- 🎨 Modern and beautiful UI
- ⚡ High-performance architecture
- 🔧 Extensible agent framework

## Technology Stack

### Backend
- FastAPI - High-performance Python web framework
- WebSocket - Real-time communication
- LangChain - AI conversation framework
- DeepAgents - Custom agent framework
- Multiple LLM integrations

### Frontend
- React - UI framework
- TypeScript - Type safety
- Tailwind CSS - Styling framework
- Vite - Build tool
- WebSocket API - Real-time communication

## Quick Start

### Using Batch Scripts (Recommended)

Windows users can directly use the following batch scripts:

```bash
# Install dependencies and create virtual environment
install.bat

# Start both frontend and backend services
start.bat

# Stop both frontend and backend services
stop.bat
```

### Manual Installation

#### 1. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate
```

#### 2. Install backend dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Start backend service

```bash
# From project root directory
export PYTHONPATH=/your/path/to/deepagents-edward/src;%PYTHONPATH%
cd backend
python server.py
```

The service will start at http://localhost:8000

#### 4. Install frontend dependencies

```bash
# In a new terminal, enter the frontend directory
cd frontend

# Install dependencies
npm install
```

#### 5. Start frontend development server

```bash
npm run dev
```

The frontend development server will start at http://localhost:3000

## Usage

1. Open your browser and visit http://localhost:3000 (or the port shown in your terminal)
2. Enter your questions or requests in the input box, for example:
   - "What's the weather like in Shanghai today?"
   - "Explain quantum computing in simple terms"
   - "Write a Python function to calculate factorial"

3. The system will return AI-generated answers in real-time with natural typing effect.

## Project Structure

```
deepagents-edward/
├── src/
│   ├── agents/            # AI agent implementations
│   ├── utils/             # Utility functions
│   └── test_workflow.py   # Workflow testing
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # Main application component
│   │   ├── main.tsx       # Application entry point
│   │   └── index.css      # Global styles
│   ├── index.html         # HTML template
│   ├── package.json       # Project configuration
│   ├── vite.config.ts     # Vite configuration
│   ├── tailwind.config.js # Tailwind configuration
│   └── postcss.config.js  # PostCSS configuration
├── src/                   # Weather agent source code
└── requirements.txt        # Python dependencies
```

## API Endpoints

- `GET /` - API information
- `POST /chat` - Chat with weather agent
- `WebSocket /ws/{session_id}` - WebSocket streaming conversation
- `GET /health` - Health check
- `GET /chat` - Simple frontend interface

## Extension Features

Future features to add:
- Multi-language support
- Agent marketplace
- Custom agent creation
- Advanced analytics dashboard
- User account system
- Personalized settings
- Integration with external services

## Deployment Instructions

### Backend Deployment

Backend can be deployed using Docker or traditional servers:

```bash
# Deploy using Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
```

### Frontend Deployment

Build production version:

```bash
cd frontend
npm run build
```

The built files are in the `dist` directory and can be deployed to any static file server.