# Weather Assistant Web Application

This is a weather assistant web application based on FastAPI and React, providing conversational weather query services.

## Features

- 🌤️ Real-time weather query
- 💬 Conversational interface
- 🔄 Streaming responses
- 📱 Responsive design
- 🎨 Modern and beautiful UI

## Technology Stack

### Backend
- FastAPI - High-performance Python web framework
- WebSocket - Real-time communication
- LangChain - AI conversation framework
- Open-Meteo API - Weather data source

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
install_simple.bat

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

1. Open your browser and visit http://localhost:3000
2. Enter weather-related questions in the input box, for example:
   - "What's the weather like in Shanghai today?"
   - "How's the weather in Beijing for the next three days?"
   - "Will it rain in New York tomorrow?"

3. The system will return weather information and answers in real-time.

## Project Structure

```
deepagents-demo/
├── backend/
│   ├── server.py          # FastAPI server
│   ├── static/
│   │   └── index.html     # Simple frontend interface
│   └── README.md          # Backend documentation
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
- Weather warning notifications
- Historical weather query
- Weather chart visualization
- User account system
- Personalized settings

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