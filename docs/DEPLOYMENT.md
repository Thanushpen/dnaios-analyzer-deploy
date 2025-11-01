# 🚀 Deployment Guide

Complete guide to deploying DNAiOS Architecture Analyzer to production.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Render.com)](#backend-deployment)
3. [Frontend Deployment (Vercel)](#frontend-deployment)
4. [Alternative: Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ [GitHub Account](https://github.com) (free)
- ✅ [Render.com Account](https://render.com) (free tier available)
- ✅ [Vercel Account](https://vercel.com) (free tier available)

### Tools Needed
```bash
git --version        # Git for version control
python --version     # Python 3.11+
node --version       # Node.js (for Vercel CLI)
```

---

## Backend Deployment (Render.com)

### Step 1: Push to GitHub

```bash
# Initialize git repository
cd dnaios-analyzer
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/dnaios-analyzer.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**
   - Authorize Render to access your repos
   - Select `dnaios-analyzer`

4. **Configure the service:**
   ```yaml
   Name: dnaios-analyzer-api
   Region: Oregon (or closest to you)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python analyzer.py
   Instance Type: Free
   ```

5. **Advanced Settings:**
   ```yaml
   Environment Variables:
     PYTHON_VERSION: 3.11.0
     PORT: 5001
   
   Health Check Path: /health
   Auto-Deploy: Yes
   ```

6. **Click "Create Web Service"**

7. **Wait for deployment** (5-10 minutes)

8. **Your API is live!**
   ```
   https://dnaios-analyzer-api.onrender.com
   ```

### Step 3: Test the Backend

```bash
# Test health endpoint
curl https://dnaios-analyzer-api.onrender.com/health

# Expected response:
# {"status":"healthy","version":"4.9-optimized",...}
```

---

## Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Update Frontend Configuration

Create `frontend/.env`:
```env
VITE_API_URL=https://dnaios-analyzer-api.onrender.com
```

Update `frontend/index.html` to use the environment variable:
```javascript
// Replace hardcoded API URL with:
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';
```

### Step 3: Deploy to Vercel

```bash
# Navigate to project root
cd dnaios-analyzer

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# ? Set up and deploy "~/dnaios-analyzer"? [Y/n] y
# ? Which scope? Your username
# ? Link to existing project? [y/N] n
# ? What's your project's name? dnaios-analyzer
# ? In which directory is your code located? ./

# For production:
vercel --prod
```

### Step 4: Configure Vercel Project

Go to [Vercel Dashboard](https://vercel.com/dashboard):

1. **Select your project**
2. **Settings → Environment Variables**
3. **Add:**
   ```
   VITE_API_URL=https://dnaios-analyzer-api.onrender.com
   ```
4. **Redeploy**

### Step 5: Your App is Live!

```
https://dnaios-analyzer.vercel.app
```

---

## Docker Deployment

### Option 1: Docker Compose (Backend + Frontend)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5001:5001"
    environment:
      - PYTHON_VERSION=3.11.0
      - PORT=5001
    volumes:
      - ./backend:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
    depends_on:
      - backend
```

Run:
```bash
docker-compose up -d
```

### Option 2: Backend Only

```bash
cd backend
docker build -t dnaios-analyzer .
docker run -p 5001:5001 dnaios-analyzer
```

---

## Environment Configuration

### Backend (.env)

```env
# Server Configuration
PORT=5001
HOST=0.0.0.0

# Upload Limits
MAX_ZIP_SIZE=4294967296  # 4GB
MAX_SINGLE_FILE_SIZE=52428800  # 50MB
MAX_FILES=100000

# Memory Settings
MEMORY_WARNING_THRESHOLD=14000  # 14GB in MB

# Security
ALLOWED_ORIGINS=https://dnaios-analyzer.vercel.app,http://localhost:8000

# Optional: Database
DATABASE_URL=sqlite:///./analyzer.db
```

### Frontend (.env)

```env
# API Configuration
VITE_API_URL=https://dnaios-analyzer-api.onrender.com

# Optional: Analytics
VITE_GA_ID=G-XXXXXXXXXX
```

---

## Troubleshooting

### Backend Issues

**Problem: Build fails on Render**
```bash
Solution:
1. Check requirements.txt is in backend/
2. Verify Python version (3.11)
3. Check Render logs: Dashboard → Service → Logs
```

**Problem: 502 Bad Gateway**
```bash
Solution:
1. Check health endpoint: /health
2. Verify port 5001 is exposed
3. Check memory usage (may need paid tier for >512MB)
```

**Problem: Large file uploads fail**
```bash
Solution:
1. Upgrade to paid Render plan
2. Or use Railway.app (higher limits)
3. Or deploy to your own VPS
```

### Frontend Issues

**Problem: CORS errors**
```bash
Solution:
Add to backend analyzer.py:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problem: API not connecting**
```bash
Solution:
1. Check VITE_API_URL in .env
2. Verify backend is running: curl [API_URL]/health
3. Check browser console for errors
```

### Performance Issues

**Problem: Slow analysis**
```bash
Solution:
1. Upgrade Render instance type
2. Enable caching
3. Reduce MAX_FILES limit
4. Filter out unnecessary directories
```

---

## Production Checklist

- [ ] Backend deployed and health check passing
- [ ] Frontend deployed and loading correctly
- [ ] API URL configured in frontend
- [ ] CORS settings verified
- [ ] SSL/HTTPS enabled (automatic on Render/Vercel)
- [ ] Environment variables set
- [ ] Error logging configured
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] GitHub repository public/private as desired

---

## Monitoring

### Render Monitoring

```bash
# View logs
render logs [service-name] --tail

# Check metrics
Dashboard → Service → Metrics
```

### Health Checks

```bash
# Automated health monitoring
curl -f https://dnaios-analyzer-api.onrender.com/health || \
  curl -X POST [YOUR_SLACK_WEBHOOK] -d '{"text":"API is down!"}'
```

---

## Scaling

### When to Scale

- Upload size > 4GB needed
- Memory usage > 80%
- Request timeout issues
- Multiple concurrent users

### Options

1. **Render**: Upgrade to paid tier ($7+/month)
2. **Railway**: Higher free tier limits
3. **AWS/GCP**: Full control, complex setup
4. **DigitalOcean**: Simple VPS ($5+/month)

---

## Support

Need help? Contact:
- 📧 thanushpen@gmail.com
- 🐙 GitHub Issues: [Create Issue](https://github.com/thanushpen/dnaios-analyzer/issues)

---

**Good luck with your deployment! 🚀**
