# 🧬 DNAiOS Architecture Analyzer

> **Advanced Software Architecture Analysis Platform** - Analyze up to 20,000 files and 4GB of code for distributed systems (~2000 agents)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🌟 Overview

**DNAiOS Architecture Analyzer** is a powerful tool for analyzing large-scale software architectures. Built with FastAPI and featuring an interactive Monaco Editor interface, it provides deep insights into code complexity, dependencies, and system structure.

### ✨ Key Features

- 📊 **Complexity Analysis** - Radon-powered complexity metrics and maintainability index
- 🔗 **Dependency Graphing** - Visual node/edge graphs with force-directed layouts
- 💻 **Monaco Editor Integration** - Syntax highlighting and code editing
- 🚀 **High Performance** - Handles up to 4GB uploads and 100,000 files
- 🔒 **Secure API** - CORS and JWT support
- 🎨 **3D Visualizations** - Three.js powered interactive graphs
- 🧠 **Memory Monitoring** - Real-time memory usage tracking
- 📦 **Dead Code Detection** - Identifies unused functions and modules
- ⚡ **AST Analysis** - Deep Python Abstract Syntax Tree parsing

---

## 🖼️ Screenshots

### Interactive Architecture Visualization
*Radial layout view showing module dependencies with real-time analysis*

### Hierarchical Code Structure
*Tree-based navigation with detailed module information*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (Vercel)                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  Monaco Editor │ Three.js │ Interactive UI  │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS/REST API
                     ▼
┌─────────────────────────────────────────────────────┐
│                BACKEND API (Render.com)             │
│  ┌──────────────────────────────────────────────┐  │
│  │  FastAPI │ Radon │ AST Parser │ SQLite     │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **16GB RAM recommended** (4GB minimum)
- **pip** package manager

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/thanushpen/dnaios-analyzer.git
cd dnaios-analyzer
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Run the backend**
```bash
python analyzer.py
```

The backend will start on `http://localhost:5001`

4. **Open the frontend**
```bash
# Simply open frontend/index.html in your browser
# Or serve with a local server:
cd frontend
python -m http.server 8000
```

Visit `http://localhost:8000`

---

## 🌐 Deployment

### Backend Deployment (Render.com)

1. **Create a Render account** at [render.com](https://render.com)

2. **Connect your GitHub repository**

3. **Create a new Web Service**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python analyzer.py`
   - **Environment**: Python 3.11

4. **Set environment variables** (if needed)

5. **Deploy!** Your backend will be available at:
   ```
   https://your-app-name.onrender.com
   ```

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy to Vercel**
```bash
cd frontend
vercel
```

3. **Update API URL**
   - Create `.env` file in frontend:
   ```env
   VITE_API_URL=https://your-backend.onrender.com
   ```

4. **Your app is live!**
   ```
   https://your-app.vercel.app
   ```

---

## 📊 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "4.9-optimized",
  "radon": true,
  "psutil": true,
  "memory_monitoring": true,
  "limits": {
    "max_zip_gb": 4.0,
    "max_single_file_mb": 50,
    "max_files": 100000
  }
}
```

### Analyze Project
```http
POST /analyze
Content-Type: multipart/form-data

file: <zip_file>
symbol_level: true/false
```

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "module_details": {...},
  "folder_structure": {...}
}
```

### Memory Status
```http
GET /memory
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Radon** - Code complexity metrics
- **PSUtil** - System and memory monitoring
- **Python AST** - Abstract Syntax Tree parsing
- **SQLite** - Lightweight data storage

### Frontend
- **Monaco Editor** - VS Code's editor
- **Three.js** - 3D visualizations
- **Vanilla JavaScript** - No framework overhead
- **HTML5/CSS3** - Modern web standards

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Max Upload Size | 4 GB |
| Max Files | 100,000 |
| Max Single File | 50 MB |
| Recommended RAM | 16 GB |
| Minimum RAM | 4 GB |
| Analysis Speed | ~2000 files/min |

---

## 🎯 Use Cases

### 1. **Large-Scale Systems Analysis**
- Analyze distributed systems with thousands of components
- Identify bottlenecks and complexity hotspots
- Visualize inter-module dependencies

### 2. **Code Quality Assessment**
- Calculate maintainability index
- Detect dead code
- Measure cyclomatic complexity

### 3. **Architecture Documentation**
- Generate visual dependency graphs
- Export architecture diagrams
- Create AI-ready project summaries

### 4. **Cybersecurity Audits**
- Monitor encryption protocols
- Detect security vulnerabilities
- Analyze attack surfaces

---

## 📝 Configuration

### Environment Variables

Create a `.env` file:

```env
# Backend
PORT=5001
MAX_UPLOAD_SIZE=4294967296  # 4GB in bytes
MAX_FILES=100000
MEMORY_WARNING_THRESHOLD=14000  # 14GB in MB

# Frontend
VITE_API_URL=http://localhost:5001
```

### Skipped Directories

The analyzer automatically skips:
- `venv/`, `env/`, `.venv/`
- `node_modules/`
- `__pycache__/`
- `.git/`, `.svn/`
- `build/`, `dist/`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Thanush GANESH**

- 📧 Email: thanushpen@gmail.com
- 📍 Location: Nevers, France
- 💼 LinkedIn: [linkedin.com/in/thanush-ganesh](https://linkedin.com/in/thanush-ganesh)
- 🐙 GitHub: [@thanushpen](https://github.com/thanushpen)

---

## 🙏 Acknowledgments

- Built with ❤️ for the tech community
- Powered by FastAPI and Monaco Editor
- Inspired by the need for better architecture visualization tools

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/thanushpen/dnaios-analyzer/issues) page
2. Create a new issue with detailed information
3. Contact: thanushpen@gmail.com

---

## 🗺️ Roadmap

- [ ] WebSocket support for real-time analysis updates
- [ ] Multi-language support (JavaScript, Java, C++)
- [ ] Export to PDF/SVG
- [ ] Integration with CI/CD pipelines
- [ ] Machine learning-based code smell detection
- [ ] Collaborative analysis features

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

Made with 💜 by [Thanush GANESH](https://github.com/thanushpen)

</div>
