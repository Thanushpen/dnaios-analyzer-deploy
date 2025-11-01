# 🚀 Quick Start Guide

Get DNAiOS Architecture Analyzer running in **5 minutes**!

---

## ⚡ Super Quick Start

### Linux/Mac:
```bash
./start.sh
```

### Windows:
```batch
start.bat
```

Then open: **http://localhost:8000**

---

## 📦 What's Included

```
dnaios-analyzer/
├── 🐍 backend/          → FastAPI server (Python)
├── 🎨 frontend/         → Web UI (HTML/JS)
├── 📚 docs/             → Full documentation
├── ⚙️  .github/         → CI/CD workflows
├── 📄 README.md         → Main docs
├── 🚀 start.sh          → Quick start (Unix)
└── 🚀 start.bat         → Quick start (Windows)
```

---

## 🎯 Choose Your Path

### 1. 👨‍💻 Just Want to Try It?

**Local Development** (5 minutes):
```bash
# 1. Run quick start
./start.sh

# 2. Open browser
open http://localhost:8000

# 3. Upload a ZIP file with Python code
```

---

### 2. 🌐 Want to Deploy Online?

**Deploy to Production** (15 minutes):

**Step 1:** Backend (Render.com)
```bash
1. Push to GitHub
2. Connect to Render.com
3. Deploy from backend/ folder
```
→ See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

**Step 2:** Frontend (Vercel)
```bash
1. Install Vercel CLI: npm i -g vercel
2. Run: vercel
3. Done!
```
→ See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

### 3. 🔧 Want to Develop?

**Full Dev Setup** (10 minutes):
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Start developing!
python analyzer.py
```
→ See [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)

---

## 📋 Prerequisites

| Tool | Version | Why? |
|------|---------|------|
| **Python** | 3.11+ | Backend server |
| **pip** | Latest | Python packages |
| **Git** | Latest | Version control |

### Check Installation:
```bash
python --version  # Should be 3.11+
pip --version
git --version
```

---

## 🎓 First Steps Tutorial

### 1. Start the Server
```bash
./start.sh
```

### 2. Create Test Project
```bash
mkdir test-project
echo "print('Hello World')" > test-project/main.py
zip -r test.zip test-project/
```

### 3. Upload & Analyze
1. Open http://localhost:8000
2. Click "📁 Upload"
3. Select test.zip
4. Click "Analyze"
5. See the magic! ✨

---

## 💡 Common Use Cases

### Analyze Django Project
```bash
cd my-django-project
zip -r ../django.zip . -x "venv/*" -x "*.pyc"
# Upload django.zip to analyzer
```

### Analyze Flask API
```bash
cd my-flask-api
zip -r ../flask.zip . -x "venv/*" -x "__pycache__/*"
# Upload flask.zip to analyzer
```

### Analyze ML Project
```bash
cd ml-project
zip -r ../ml.zip . -x "data/*" -x "models/*"
# Upload ml.zip to analyzer
```

---

## 🐛 Troubleshooting

### Problem: Port already in use
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Or change port in backend/analyzer.py
```

### Problem: Module not found
```bash
# Install missing dependencies
cd backend
pip install -r requirements.txt
```

### Problem: Can't access http://localhost:8000
```bash
# Check if server is running
ps aux | grep python

# Restart the server
./start.sh
```

### Problem: CORS errors
```bash
# Make sure backend is running FIRST
# Then start frontend
```

---

## 📚 Learn More

| Document | What's Inside |
|----------|---------------|
| [README.md](README.md) | Full overview & features |
| [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) | Development guide |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deployment guide |
| [docs/API.md](docs/API.md) | API documentation |

---

## 🎥 Video Tutorial

_(Coming soon: Video walkthrough of installation and usage)_

---

## ❓ Need Help?

- 📧 Email: thanushpen@gmail.com
- 🐙 GitHub Issues: [Create Issue](https://github.com/thanushpen/dnaios-analyzer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/thanushpen/dnaios-analyzer/discussions)

---

## ⭐ Like It?

If you find this useful:
1. ⭐ Star the repo on GitHub
2. 🐦 Share on Twitter/LinkedIn
3. 🤝 Contribute improvements

---

## 🗺️ What's Next?

1. ✅ Got it running? Check out the [full README](README.md)
2. 🚀 Want to deploy? See [DEPLOYMENT.md](docs/DEPLOYMENT.md)
3. 🔧 Want to contribute? See [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)

---

<div align="center">

**Happy analyzing! 🧬**

Made with 💜 by [Thanush GANESH](https://github.com/thanushpen)

</div>
