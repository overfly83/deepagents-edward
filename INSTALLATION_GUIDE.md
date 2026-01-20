# DeepAgents Demo Installation Guide

## Quick Start (Recommended)

### Windows Users

1. **Download the project** to your local machine
2. **Run the installation script**:
   - Double-click `install_fresh.bat` to create a fresh installation
   - Or double-click `install_simple.bat` for a simple installation
3. **Start the application**:
   - Double-click `start.bat` to start both frontend and backend

### Linux/Mac Users

1. **Download the project** to your local machine
2. **Open terminal** and navigate to the project directory
3. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   ```
4. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```
5. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. **Start backend server**:
   ```bash
   python -m uvicorn backend.server:app --reload
   ```
7. **Start frontend** (in a new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Detailed Installation Steps

### 1. Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher (for frontend)
- Git (optional, for cloning the repository)

### 2. Backend Installation

#### Create Virtual Environment

```bash
# Windows
python -m venv .venv

# Linux/Mac
python3 -m venv .venv
```

#### Activate Virtual Environment

```bash
# Windows
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

#### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Start Backend Server

```bash
# Development mode (with auto-reload)
python -m uvicorn backend.server:app --reload

# Production mode (with multiple workers)
python -m uvicorn backend.server:app --workers 4 --log-level info
```

Backend will be available at http://localhost:8000

### 3. Frontend Installation

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Start Development Server

```bash
npm run dev
```

Frontend will be available at http://localhost:3000

#### Build for Production

```bash
npm run build
```

## Troubleshooting

### Common Issues

1. **Python not found**:
   - Make sure Python is installed and added to your PATH
   - Download Python from https://www.python.org/downloads/

2. **Permission denied**:
   - Run the installation as administrator/root
   - Or install in a directory where you have write permissions

3. **Port already in use**:
   - For backend: Change port with `--port 8001`
   - For frontend: Change port in `vite.config.ts`

4. **Module not found**:
   - Make sure the virtual environment is activated
   - Run `pip list` to check installed packages
   - Reinstall dependencies with `pip install -r requirements.txt`

### API Keys Configuration

If you need to configure API keys:
1. Copy `.env.example` to `.env`
2. Edit `.env` and add your API keys
3. Restart the application

## Project Structure

```
deepagents-demo/
├── backend/           # Backend FastAPI application
│   ├── server.py      # Main server file
│   └── static/        # Static files
├── frontend/          # React frontend application
│   ├── src/           # Source code
│   └── public/        # Public assets
├── src/               # DeepAgents source code
│   └── agents/        # AI agents
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## Available Scripts

### Backend

- `python -m uvicorn backend.server:app --reload` - Start backend in development mode
- `python -m pytest` - Run backend tests

### Frontend

- `npm run dev` - Start frontend development server
- `npm run build` - Build frontend for production
- `npm run lint` - Lint frontend code

### Batch Scripts (Windows)

- `install_simple.bat` - Simple installation
- `install_fresh.bat` - Fresh installation in new window
- `start.bat` - Start both frontend and backend
- `stop.bat` - Stop both frontend and backend

## Support

If you encounter any issues during installation, please:
1. Check this guide thoroughly
2. Verify all prerequisites are met
3. Try the fresh installation script (`install_fresh.bat`)
4. Review the error logs carefully