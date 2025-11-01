# 📡 API Documentation

Complete API reference for DNAiOS Architecture Analyzer.

---

## Base URL

```
Development: http://localhost:5001
Production:  https://your-app.onrender.com
```

---

## Authentication

Currently no authentication required. For production, implement JWT:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/analyze")
async def analyze(token: str = Depends(security)):
    # Verify token
    pass
```

---

## Endpoints

### 1. Health Check

Check if the API is running and get system information.

**Endpoint:** `GET /health`

**Response:**
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

**Example:**
```bash
curl http://localhost:5001/health
```

---

### 2. Analyze Project

Upload and analyze a ZIP file containing Python code.

**Endpoint:** `POST /analyze`

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | ZIP file containing Python code |
| symbol_level | Boolean | No | Include function-level analysis (default: false) |

**Request:**
```bash
curl -X POST http://localhost:5001/analyze \
  -F "file=@myproject.zip" \
  -F "symbol_level=true"
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "module_name",
      "label": "Module Name",
      "kind": "module",
      "path": "path/to/module.py",
      "icon": "📄",
      "x": 100,
      "y": 200
    }
  ],
  "edges": [
    {
      "from": "module_a",
      "to": "module_b",
      "type": "imports",
      "strength": 1
    }
  ],
  "module_details": {
    "module_name": {
      "path": "path/to/module.py",
      "type": "module",
      "role": "Core module providing main functionality",
      "lines": 500,
      "complexity": 15,
      "mi": 75.5,
      "imports": ["os", "sys", "json"],
      "functions": [
        {
          "name": "main",
          "complexity": 5,
          "mi": 80.2,
          "lines": 50,
          "calls": ["helper_func"],
          "called_by": [],
          "is_entrypoint": true
        }
      ],
      "classes": 3,
      "entrypoints": ["main"],
      "dead_functions": [],
      "source": "# Full source code here..."
    }
  },
  "folder_structure": {
    "name": "root",
    "type": "folder",
    "children": {},
    "files": []
  },
  "summary": {
    "total_modules": 50,
    "total_functions": 200,
    "total_classes": 30,
    "total_lines": 10000,
    "avg_complexity": 8.5,
    "avg_mi": 72.3
  }
}
```

**Error Responses:**

```json
// File too large
{
  "detail": "ZIP file exceeds 4GB limit"
}

// Invalid file
{
  "detail": "Uploaded file is not a valid ZIP archive"
}

// Memory exceeded
{
  "detail": "Memory usage exceeds safe threshold"
}
```

---

### 3. Memory Status

Get current memory usage statistics.

**Endpoint:** `GET /memory`

**Response:**
```json
{
  "process": {
    "rss_mb": 245.7,
    "vms_mb": 512.3,
    "percent": 1.5
  },
  "system": {
    "total_gb": 16.0,
    "available_gb": 12.5,
    "used_gb": 3.5,
    "percent": 21.9
  },
  "threshold": {
    "warning_mb": 14000,
    "warning_gb": 13.7
  }
}
```

**Example:**
```bash
curl http://localhost:5001/memory
```

---

## Data Models

### Node

```typescript
interface Node {
  id: string;           // Unique identifier
  label: string;        // Display name
  kind: string;         // "module", "class", "function", etc.
  path: string;         // File path
  icon: string;         // Emoji icon
  x: number;            // Graph position X
  y: number;            // Graph position Y
}
```

### Edge

```typescript
interface Edge {
  from: string;         // Source node ID
  to: string;           // Target node ID
  type: string;         // "imports", "calls", "defines", "external"
  strength: number;     // Connection strength (1-5)
}
```

### ModuleDetail

```typescript
interface ModuleDetail {
  path: string;
  type: string;
  role: string;
  lines: number;
  complexity: number;
  mi: number;
  imports: string[];
  functions: FunctionInfo[];
  classes: number;
  entrypoints: string[];
  dead_functions: string[];
  source: string;
}
```

### FunctionInfo

```typescript
interface FunctionInfo {
  name: string;
  complexity: number;
  mi: number;
  lines: number;
  calls: string[];
  called_by: string[];
  is_entrypoint: boolean;
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 413 | Payload Too Large - File exceeds limits |
| 422 | Unprocessable Entity - Invalid file format |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Memory exceeded |

---

## Rate Limiting

Current implementation: **No rate limiting**

For production, implement rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze(...):
    pass
```

---

## CORS Configuration

Current allowed origins:

```python
allow_origins=[
    "http://localhost:8000",
    "http://localhost:3000",
    "https://*.vercel.app"
]
```

To modify, edit `analyzer.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## WebSocket Support (Future)

Planned for real-time analysis updates:

```javascript
const ws = new WebSocket('ws://localhost:5001/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Analysis progress:', data.progress);
};
```

---

## Example Integration

### JavaScript/Fetch

```javascript
async function analyzeProject(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('symbol_level', 'true');
  
  const response = await fetch('http://localhost:5001/analyze', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }
  
  return await response.json();
}
```

### Python/Requests

```python
import requests

def analyze_project(zip_path):
    with open(zip_path, 'rb') as f:
        files = {'file': f}
        data = {'symbol_level': 'true'}
        
        response = requests.post(
            'http://localhost:5001/analyze',
            files=files,
            data=data
        )
        
        return response.json()
```

### cURL

```bash
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: multipart/form-data" \
  -F "file=@project.zip" \
  -F "symbol_level=true" \
  -o result.json
```

---

## Performance Tips

### 1. Optimize File Size
```bash
# Remove unnecessary files before zipping
zip -r project.zip . -x "*.pyc" -x "__pycache__/*" -x "venv/*"
```

### 2. Use Symbol Level Wisely
```javascript
// For quick overview, disable symbol_level
formData.append('symbol_level', 'false');

// For detailed analysis, enable it
formData.append('symbol_level', 'true');
```

### 3. Monitor Memory
```bash
# Check before large uploads
curl http://localhost:5001/memory
```

---

## Testing

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from analyzer import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze():
    with open("test.zip", "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": f},
            data={"symbol_level": "true"}
        )
    assert response.status_code == 200
```

---

## Changelog

### v4.9 (Current)
- ✅ 4GB upload support
- ✅ Memory monitoring
- ✅ Auto-skip venv/node_modules
- ✅ Full source code in response
- ✅ Monaco Editor integration

### Planned (v5.0)
- 🔄 WebSocket support
- 🔄 Multi-language support
- 🔄 PDF export
- 🔄 Authentication
- 🔄 Rate limiting

---

## Support

- 📧 Email: thanushpen@gmail.com
- 🐙 GitHub: [Issues](https://github.com/thanushpen/dnaios-analyzer/issues)
- 📚 Docs: [Full Documentation](https://github.com/thanushpen/dnaios-analyzer)

---

**Last Updated:** November 2025
