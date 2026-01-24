# DeepAgents AI Platform - Production Deployment Guide

## 1. Environment Preparation

### 1.1 Install Dependencies

Ensure all necessary dependencies are installed:

```bash
pip install -r requirements.txt
pip install -r requirements-backend.txt
```

### 1.2 Configure Environment Variables

Create a `.env` file in the project root directory and configure the necessary environment variables:

```env
# ZhipuAI API Key (required for the LLM)
# Get your free API key at: https://open.bigmodel.cn/api/key
ZHIPU_API_KEY=your_api_key_here

# Optional environment variables
# OPENAI_API_KEY=your_openai_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here
```

## 2. Build the Frontend

Ensure the frontend code is built and deployed to the backend's static directory:

```bash
cd frontend
npm install
npm run build
```

The built files will be automatically copied to the `backend/static` directory.

## 3. Start the Production Server

### 3.1 Windows Environment

On Windows, use Uvicorn as the production server:

```bash
# Start server with 4 worker processes
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

### 3.2 Linux/Unix Environment

On Linux/Unix, it's recommended to use Gunicorn as the production-grade ASGI server:

```bash
# Install Gunicorn
pip install gunicorn

# Start server with 4 worker processes
python -m gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app --bind 0.0.0.0:8000 --log-level info
```

## 4. Server Configuration Recommendations

### 4.1 Port Configuration

The default port is 8000, which can be modified as needed. In production environments, it's recommended to use port 80 or 443 (requires administrator privileges):

```bash
# Use port 80 (requires administrator privileges)
python -m uvicorn backend.server:app --host 0.0.0.0 --port 80 --workers 4 --log-level info
```

### 4.2 Number of Worker Processes

It's recommended to set the number of worker processes to 2-4 times the number of CPU cores. For example, for a 4-core CPU, you can set 8-16 worker processes.

### 4.3 Log Configuration

In production environments, it's recommended to output logs to a file with an appropriate log level:

```bash
# Output logs to file
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info --log-file /var/log/deepagents/demo.log
```

## 5. Security Configuration

### 5.1 Configure HTTPS

In production environments, it's strongly recommended to use HTTPS:

```bash
# Use self-signed certificate (for testing only)
python -m uvicorn backend.server:app --host 0.0.0.0 --port 443 --workers 4 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

For production environments, it's recommended to use free certificates provided by certificate authorities like Let's Encrypt.

### 5.2 Configure CORS

In the `backend/server.py` file, the current CORS configuration allows all origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
```

In production environments, it's recommended to restrict access to specific origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://your-domain.com'],  # Restrict to specific domain
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
)
```

## 6. Monitoring and Maintenance

### 6.1 Monitor Server Status

Use system tools or third-party monitoring services (such as Prometheus + Grafana) to monitor server status and performance.

### 6.2 Regularly Update Dependencies

Regularly update project dependencies to fix security vulnerabilities and obtain new features:

```bash
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements-backend.txt
```

## 7. Troubleshooting

### 7.1 Common Issues

1. **API Key Error**: Ensure the API Key in the `.env` file is correctly configured.
2. **Port Already in Use**: Use `netstat -tuln` or `lsof -i :8000` to check for port conflicts and use a different port.
3. **Dependency Version Conflict**: Use a virtual environment to isolate project dependencies or specify specific versions of dependency packages.

### 7.2 View Logs

View server logs to troubleshoot issues:

```bash
# View real-time logs
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --workers 4 --log-level debug
```

## 8. Docker Deployment (Optional)

### 8.1 Create a Dockerfile

Create a `Dockerfile` in the project root directory:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-backend.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-backend.txt

# Copy project files
COPY . .

# Build frontend
RUN cd frontend && npm install && npm run build

# Expose port
EXPOSE 8000

# Start server
CMD ["python", "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 8.2 Build Docker Image

```bash
docker build -t deepagents-demo .
```

### 8.3 Run Docker Container

```bash
docker run -d -p 8000:8000 --env-file .env deepagents-demo
```

## 9. Best Practices

1. **Use Virtual Environments**: Create an isolated virtual environment for the project to avoid dependency conflicts.
2. **Configure Automated Testing**: Run tests regularly to ensure code quality.
3. **Use CI/CD**: Set up continuous integration and deployment processes to automate building and deployment.
4. **Backup Data**: Regularly backup important data and configuration files.
5. **Use Load Balancing**: For high-traffic applications, use load balancers to distribute requests.
6. **Configure Firewalls**: Restrict server access by only opening necessary ports.

---

By following these steps, you can safely and efficiently deploy and run the DeepAgents AI Platform in a production environment.