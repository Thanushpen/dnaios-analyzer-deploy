# 💻 Local Development Guide

Complete guide to running DNAiOS Architecture Analyzer on your local machine.

---

## 🎯 Quick Start (5 minutes)

```bash
# 1. Clone the repo
git clone https://github.com/thanushpen/dnaios-analyzer.git
cd dnaios-analyzer

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Run backend
python analyzer.py

# 4. Open frontend (in new terminal)
cd ../frontend
python -m http.server 8000

# 5. Visit http://localhost:8000
```

---

## 📋 Prerequisites

### Required Software

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.11+ | [python.org](https://python.org) |
| pip | Latest | Included with Python |
| Git | Latest | [git-scm.com](https://git-scm.com) |

### Optional but Recommended

- **VS Code** - Best IDE for this project
- **Postman** - API testing
- **Docker** - Containerization

---

## 🔧 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/thanushpen/dnaios-analyzer.git
cd dnaios-analyzer
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Expected output:
```
Successfully installed:
- fastapi==0.109.0
- uvicorn==0.27.0
- radon==6.0.1
- psutil==5.9.8
- python-multipart==0.0.6
```

---

## 🚀 Running the Application

### Backend Server

```bash
cd backend
python analyzer.py
```

Expected output:
```
================================================================================
DNAiOS Architecture Analyzer v4.9 - Optimized for 16GB RAM
================================================================================

Starting on http://0.0.0.0:5001

Optimizations:
  ✅ 4 GB maximum upload size
  ✅ Memory monitoring with safety checks
  ✅ Auto-skip venv/node_modules/build directories
  ✅ Progress logging every 500 modules
  ✅ Aggressive garbage collection
  ✅ Monaco Editor integration ready
  ✅ Full Python source code available per module

Status:
  Radon: ✅ Available
  PSUtil: ✅ Available

Limits:
  Max ZIP: 4 GB
  Max single file: 50 MB
  Max files: 100,000
  Memory warning: 14 GB
================================================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5001
```

### Frontend Server

Open a new terminal:

```bash
cd frontend
python -m http.server 8000
```

Or use any static server:
```bash
# Using Node.js
npx serve .

# Using PHP
php -S localhost:8000

# Or just open index.html in browser (with CORS issues)
```

---

## 🧪 Testing

### Test Backend Health

```bash
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "4.9-optimized",
  "radon": true,
  "psutil": true,
  "file_contents_support": true,
  "memory_monitoring": true,
  "current_memory_mb": "245.7",
  "limits": {
    "max_zip_gb": 4.0,
    "max_single_file_mb": 50.0,
    "max_files": 100000
  }
}
```

### Test Analysis Endpoint

```bash
# Create a test zip file with some Python code
curl -X POST http://localhost:5001/analyze \
  -F "file=@test_project.zip" \
  -F "symbol_level=true"
```

### Test Memory Endpoint

```bash
curl http://localhost:5001/memory
```

---

## 🛠️ Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

Edit files in `backend/` or `frontend/`

### 3. Test Locally

```bash
# Backend tests
cd backend
python -m pytest

# Manual testing
python analyzer.py
```

### 4. Commit and Push

```bash
git add .
git commit -m "Add: my new feature"
git push origin feature/my-new-feature
```

---

## 📁 Project Structure

```
dnaios-analyzer/
├── backend/
│   ├── analyzer.py           # Main FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Docker configuration
│   └── .env                 # Environment variables (create this)
│
├── frontend/
│   ├── index.html           # Main UI
│   └── .env                 # Frontend config (create this)
│
├── docs/
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── LOCAL_DEVELOPMENT.md # This file
│
├── .gitignore              # Git ignore rules
├── .env.example            # Example environment variables
├── README.md               # Main documentation
├── render.yaml             # Render.com config
└── vercel.json             # Vercel config
```

---

## ⚙️ Configuration

### Backend Configuration

Create `backend/.env`:

```env
# Server
PORT=5001
HOST=0.0.0.0

# Uploads
MAX_ZIP_SIZE=4294967296
MAX_SINGLE_FILE_SIZE=52428800
MAX_FILES=100000

# Memory
MEMORY_WARNING_THRESHOLD=14000

# CORS (for local development)
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Logging
LOG_LEVEL=INFO
```

### Frontend Configuration

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:5001
```

---

## 🐛 Debugging

### Enable Debug Mode

In `analyzer.py`, change:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Common Issues

**Issue: ModuleNotFoundError**
```bash
Solution:
pip install -r requirements.txt
# Or install missing package:
pip install [package-name]
```

**Issue: Port already in use**
```bash
Solution:
# Find process using port 5001
lsof -ti:5001
# Kill it
kill -9 [PID]
# Or change port in analyzer.py
```

**Issue: CORS errors in browser**
```bash
Solution:
1. Make sure backend is running
2. Check CORS middleware in analyzer.py
3. Use proper frontend URL in allow_origins
```

**Issue: Memory errors**
```bash
Solution:
1. Reduce MAX_FILES in .env
2. Close other applications
3. Increase swap space (Linux)
4. Use smaller test files
```

---

## 📊 Development Tools

### VS Code Extensions

Recommended extensions:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-azuretools.vscode-docker"
  ]
}
```

### Useful Commands

```bash
# Format code
black backend/analyzer.py

# Lint
pylint backend/analyzer.py

# Type check
mypy backend/analyzer.py

# Security check
bandit -r backend/

# Dependency check
pip-audit
```

---

## 🔍 API Testing with Postman

### Import Collection

Create `postman_collection.json`:

```json
{
  "info": {
    "name": "DNAiOS Analyzer API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:5001/health"
      }
    },
    {
      "name": "Analyze Project",
      "request": {
        "method": "POST",
        "url": "http://localhost:5001/analyze",
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "/path/to/test.zip"
            },
            {
              "key": "symbol_level",
              "value": "true",
              "type": "text"
            }
          ]
        }
      }
    },
    {
      "name": "Memory Status",
      "request": {
        "method": "GET",
        "url": "http://localhost:5001/memory"
      }
    }
  ]
}
```

---

## 🧹 Clean Up

```bash
# Remove virtual environment
deactivate
rm -rf venv/

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reset git
git clean -fdx
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Radon Documentation](https://radon.readthedocs.io/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [Three.js](https://threejs.org/docs/)

---

## 🤝 Getting Help

- 📧 Email: thanushpen@gmail.com
- 🐙 GitHub Issues: [Create Issue](https://github.com/thanushpen/dnaios-analyzer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/thanushpen/dnaios-analyzer/discussions)

---

**Happy coding! 🚀**
