# 生产环境部署文档

## 1. 环境准备

### 1.1 安装依赖

确保已安装所有必要的依赖包：

```bash
pip install -r requirements.txt
pip install -r requirements-backend.txt
```

### 1.2 配置环境变量

在项目根目录下创建`.env`文件，并配置必要的环境变量：

```env
# ZhipuAI API Key (required for the LLM)
# Get your free API key at: https://open.bigmodel.cn/api/key
ZHIPU_API_KEY=your_api_key_here

# 其他可选环境变量
# OPENAI_API_KEY=your_openai_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here
```

## 2. 构建前端

确保前端代码已经构建并部署到后端的static目录：

```bash
cd frontend
npm install
npm run build
```

构建后的文件将自动复制到`backend/static`目录。

## 3. 启动生产服务器

### 3.1 Windows环境

在Windows上，使用Uvicorn作为生产服务器：

```bash
# 使用4个工作进程启动服务器
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

### 3.2 Linux/Unix环境

在Linux/Unix上，推荐使用Gunicorn作为生产级ASGI服务器：

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务器，使用4个工作进程
python -m gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app --bind 0.0.0.0:8000 --log-level info
```

## 4. 服务器配置建议

### 4.1 端口配置

默认端口为8000，您可以根据需要修改为其他端口。在生产环境中，建议使用80或443端口（需要管理员权限）：

```bash
# 使用80端口（需要管理员权限）
python -m uvicorn backend.server:app --host 0.0.0.0 --port 80 --workers 4 --log-level info
```

### 4.2 工作进程数量

工作进程数量建议设置为CPU核心数的2-4倍。例如，对于4核CPU，可以设置8-16个工作进程。

### 4.3 日志配置

在生产环境中，建议将日志输出到文件，并配置适当的日志级别：

```bash
# 将日志输出到文件
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info --log-file /var/log/deepagents/demo.log
```

## 5. 安全配置

### 5.1 配置HTTPS

在生产环境中，强烈建议使用HTTPS：

```bash
# 使用自签名证书（仅用于测试）
python -m uvicorn backend.server:app --host 0.0.0.0 --port 443 --workers 4 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

对于生产环境，建议使用Let's Encrypt等证书颁发机构提供的免费证书。

### 5.2 配置CORS

在`backend/server.py`文件中，当前CORS配置允许所有 origins：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
```

在生产环境中，建议限制为特定的 origins：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://your-domain.com'],  # Restrict to specific domain
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
)
```

## 6. 监控与维护

### 6.1 监控服务器状态

使用系统工具或第三方监控服务（如Prometheus + Grafana）监控服务器状态和性能。

### 6.2 定期更新依赖

定期更新项目依赖，以修复安全漏洞和获取新功能：

```bash
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements-backend.txt
```

## 7. 故障排除

### 7.1 常见问题

1. **API Key错误**：确保`.env`文件中的API Key正确配置。
2. **端口被占用**：使用`netstat -tuln`或`lsof -i :8000`检查端口占用情况，并使用其他端口。
3. **依赖版本冲突**：使用虚拟环境隔离项目依赖，或指定特定版本的依赖包。

### 7.2 查看日志

查看服务器日志以排查问题：

```bash
# 实时查看日志
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --workers 4 --log-level debug
```

## 8. Docker部署（可选）

### 8.1 创建Dockerfile

在项目根目录下创建`Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt requirements-backend.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-backend.txt

# 复制项目文件
COPY . .

# 构建前端
RUN cd frontend && npm install && npm run build

# 暴露端口
EXPOSE 8000

# 启动服务器
CMD ["python", "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 8.2 构建Docker镜像

```bash
docker build -t deepagents-demo .
```

### 8.3 运行Docker容器

```bash
docker run -d -p 8000:8000 --env-file .env deepagents-demo
```

## 9. 最佳实践

1. **使用虚拟环境**：为项目创建独立的虚拟环境，避免依赖冲突。
2. **配置自动化测试**：定期运行测试，确保代码质量。
3. **使用CI/CD**：设置持续集成和部署流程，自动化构建和部署。
4. **备份数据**：定期备份重要数据和配置文件。
5. **使用负载均衡**：对于高流量应用，使用负载均衡器分发请求。
6. **配置防火墙**：限制对服务器的访问，只开放必要的端口。

---

通过以上步骤，您可以在生产环境中安全、高效地部署和运行DeepAgents Demo应用。