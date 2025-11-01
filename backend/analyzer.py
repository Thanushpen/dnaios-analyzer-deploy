"""
DNAiOS Architecture Analyzer v4.9 - Optimized for 16GB RAM
===========================================================

Optimized for 4GB max uploads with:
- Memory monitoring and safety checks
- Automatic filtering of venv/node_modules
- Garbage collection optimization
- Progress logging for large projects

Author: DNAiOS Team — Humanative AGI Systems
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from zipfile import ZipFile
from collections import defaultdict, deque
import io, os, ast, re, json, posixpath, sys, sysconfig, importlib.util
import logging
import math
import gc
from datetime import datetime

# Try to import psutil for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Try to import radon
try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if RADON_AVAILABLE:
    logger.info("✓ Radon available - complexity metrics enabled")
else:
    logger.warning("✗ Radon not installed - install with: pip install radon")

if PSUTIL_AVAILABLE:
    logger.info("✓ PSUtil available - memory monitoring enabled")
else:
    logger.warning("✗ PSUtil not installed - install with: pip install psutil")

# More aggressive garbage collection for large files
gc.set_threshold(700, 10, 10)

# ============================================================================
# CONFIGURATION - OPTIMIZED FOR 16GB RAM
# ============================================================================

MAX_FILES = 100_000
MAX_ZIP_SIZE = 4 * 1024 * 1024 * 1024  # 4 GB
MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024  # 50 MB per file
MEMORY_WARNING_THRESHOLD = 14000  # 14 GB - warn if exceeded

# Directories to automatically skip (common bloat)
SKIP_DIRECTORIES = {
    'venv', 'env', '.venv', '.env', 'virtualenv',
    'node_modules', '.git', '.svn', '.hg',
    '__pycache__', '.pytest_cache', '.tox',
    'build', 'dist', '.egg-info', 'eggs',
    '.mypy_cache', '.ruff_cache', '.cache',
    'site-packages', 'lib/python*/site-packages'
}

STDLIB_FALLBACK = {
    "sys", "os", "re", "json", "math", "time", "typing", "pathlib", "logging",
    "itertools", "functools", "collections", "asyncio", "dataclasses", "enum",
    "datetime", "random", "abc", "copy", "decimal", "fractions", "statistics",
    "threading", "multiprocessing", "subprocess", "urllib", "http", "socket",
    "ssl", "email", "html", "xml", "sqlite3", "csv", "pickle", "traceback",
    "argparse", "configparser", "contextlib", "io", "struct", "weakref"
}

TAG_PATTERN = re.compile(
    r'#\s*@(?P<tag>agent|rsi|memory|haa|data|project)\s*(name\s*:\s*(?P<n>[\w\-\.\s]+))?',
    re.IGNORECASE
)

TYPE_ICONS = {
    "agent": "🤖", "rsi": "🔄", "memory": "🧠", "haa": "⚡",
    "data": "💾", "project": "📦", "class": "🛠️", "function": "⚙️",
    "module": "📄", "external": "📦"
}

# ============================================================================
# MEMORY MONITORING
# ============================================================================

def log_memory_usage() -> float:
    """Log current memory usage and return MB used"""
    if not PSUTIL_AVAILABLE:
        return 0.0
    
    try:
        process = psutil.Process()
        mem_info = process.memory_info()
        mem_mb = mem_info.rss / 1024 / 1024
        logger.info(f"💾 Memory usage: {mem_mb:.1f} MB")
        
        if mem_mb > MEMORY_WARNING_THRESHOLD:
            logger.warning(f"⚠️ High memory usage: {mem_mb:.1f} MB (threshold: {MEMORY_WARNING_THRESHOLD} MB)")
        
        return mem_mb
    except Exception as e:
        logger.warning(f"Could not read memory: {e}")
        return 0.0

def should_skip_directory(path: str) -> bool:
    """Check if a directory path should be skipped"""
    path_lower = path.lower()
    path_parts = set(path.replace('\\', '/').split('/'))
    
    for skip_dir in SKIP_DIRECTORIES:
        if skip_dir in path_parts or skip_dir in path_lower:
            return True
    
    return False

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class FunctionDetails:
    name: str
    docstring: str
    lineno: int
    complexity: int
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)
    is_entrypoint: bool = False

@dataclass
class ComplexityMetrics:
    max_complexity: int = 0
    avg_complexity: float = 0.0
    maintainability_index: float = 0.0
    block_count: int = 0
    high_complexity_blocks: int = 0
    
    def to_dict(self) -> Dict[str, str]:
        d = {
            "MaxComplexity": str(self.max_complexity),
            "MI": f"{self.maintainability_index:.1f}",
            "Blocks": str(self.block_count)
        }
        if self.high_complexity_blocks > 0:
            d["HighComplexity"] = str(self.high_complexity_blocks)
        if self.avg_complexity > 0:
            d["AvgComplexity"] = f"{self.avg_complexity:.1f}"
        return d

@dataclass
class NodeStats:
    lines: int
    classes: int = 0
    functions: int = 0
    imports: int = 0
    complexity: Optional[ComplexityMetrics] = None
    
    def to_dict(self) -> Dict[str, str]:
        result = {"Lines": str(self.lines)}
        if self.classes > 0:
            result["Classes"] = str(self.classes)
        if self.functions > 0:
            result["Functions"] = str(self.functions)
        if self.imports > 0:
            result["Imports"] = str(self.imports)
        if self.complexity:
            result.update(self.complexity.to_dict())
        return result

@dataclass
class GraphNode:
    id: str
    kind: str
    type: str
    title: str
    path: str
    icon: str
    content: str
    project: str
    stats: Dict[str, str]
    x: float = 0.0
    y: float = 0.0
    parent: Optional[str] = None

@dataclass
class GraphEdge:
    source: str
    target: str
    type: str

# ============================================================================
# COMPLEXITY & AST VISITORS
# ============================================================================

def calculate_module_complexity(code: str, module_id: str = "") -> Tuple[ComplexityMetrics, List]:
    if not RADON_AVAILABLE or not code.strip():
        return ComplexityMetrics(), []
    
    try:
        blocks = cc_visit(code)
        
        if not blocks:
            try:
                mi = float(mi_visit(code, multi=True))
            except:
                mi = 100.0
            
            return ComplexityMetrics(
                max_complexity=1,
                avg_complexity=1.0,
                maintainability_index=round(mi, 1),
                block_count=0,
                high_complexity_blocks=0
            ), []
        
        complexities = [b.complexity for b in blocks]
        max_complexity = max(complexities)
        avg_complexity = sum(complexities) / len(complexities)
        high_count = sum(1 for c in complexities if c > 10)
        
        try:
            mi = float(mi_visit(code, multi=True))
        except:
            mi = 100.0
        
        metrics = ComplexityMetrics(
            max_complexity=max_complexity,
            avg_complexity=round(avg_complexity, 1),
            maintainability_index=round(mi, 1),
            block_count=len(blocks),
            high_complexity_blocks=high_count
        )
        
        return metrics, blocks
        
    except Exception:
        return ComplexityMetrics(), []

def map_symbol_complexities(blocks) -> Dict[str, int]:
    mapping = {}
    for block in blocks:
        classname = getattr(block, 'classname', None)
        if classname:
            key = f"{classname}.{block.name}"
        else:
            key = block.name
        mapping[key] = block.complexity
    return mapping

class ImportVisitor(ast.NodeVisitor):
    def __init__(self, parent_package: str):
        self.parent_package = parent_package
        self.imports: List[str] = []
        self.calls: Set[str] = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            base = "." * node.level + node.module if node.level else node.module
        else:
            base = "." * node.level
        
        if base.startswith("."):
            rel_depth = len(base) - len(base.lstrip("."))
            pkg_parts = self.parent_package.split(".") if self.parent_package else []
            
            if rel_depth and len(pkg_parts) >= rel_depth:
                prefix = ".".join(pkg_parts[:-rel_depth])
            else:
                prefix = self.parent_package
            
            abs_base = prefix + (("." + node.module) if node.module else "")
        else:
            abs_base = base
        
        for alias in node.names:
            if alias.name == "*":
                if abs_base:
                    self.imports.append(abs_base)
            else:
                fq = abs_base + ("." + alias.name if abs_base else alias.name)
                self.imports.append(fq if fq else alias.name)
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                self.calls.add(node.func.value.id)
        elif isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        self.generic_visit(node)

class CallGraphVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls: Dict[str, Set[str]] = defaultdict(set)
        self.current_function: Optional[str] = None
    
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_Call(self, node):
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.calls[self.current_function].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    self.calls[self.current_function].add(node.func.attr)
        self.generic_visit(node)

class EntrypointVisitor(ast.NodeVisitor):
    def __init__(self):
        self.entrypoints: Set[str] = set()
    
    def visit_If(self, node):
        if (isinstance(node.test, ast.Compare) and
            isinstance(node.test.left, ast.Name) and 
            node.test.left.id == "__name__" and
            any(isinstance(op, ast.Eq) for op in node.test.ops) and
            any(isinstance(c, ast.Constant) and c.value == "__main__" 
                for c in node.test.comparators)):
            self.entrypoints.add("__main__")
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id in ("app", "route"):
                self.entrypoints.add(node.name)
            elif isinstance(dec, ast.Attribute) and dec.attr in ("get", "post", "put", "delete", "patch", "route"):
                self.entrypoints.add(node.name)
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Attribute) and dec.func.attr in ("get", "post", "put", "delete", "patch", "route"):
                    self.entrypoints.add(node.name)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id in ("app", "route"):
                self.entrypoints.add(node.name)
            elif isinstance(dec, ast.Attribute) and dec.attr in ("get", "post", "put", "delete", "patch", "route"):
                self.entrypoints.add(node.name)
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Attribute) and dec.func.attr in ("get", "post", "put", "delete", "patch", "route"):
                    self.entrypoints.add(node.name)
        self.generic_visit(node)

def extract_symbols(tree: ast.AST) -> List[Tuple[str, str, str, int]]:
    symbols = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or f"Class {node.name}"
            symbols.append((node.name, "class", doc, node.lineno))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node) or f"Function {node.name}"
            symbols.append((node.name, "function", doc, node.lineno))
    return symbols

def is_stdlib(module_name: str) -> bool:
    try:
        if module_name in sys.builtin_module_names:
            return True
        spec = importlib.util.find_spec(module_name)
        if not spec or not spec.origin:
            return False
        stdlib_paths = [sysconfig.get_paths().get('stdlib', ''), sys.base_prefix]
        return any(spec.origin.startswith(p) for p in stdlib_paths if p)
    except Exception:
        return module_name in STDLIB_FALLBACK

def get_top_module(full_name: str) -> str:
    return full_name.split(".")[0] if full_name else ""

def module_key_from_path(root: str, filepath: str) -> str:
    rel_path = posixpath.relpath(filepath, root).rstrip("/")
    parts = rel_path.split("/")
    
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = os.path.splitext(parts[-1])[0]
    
    return ".".join(p for p in parts if p and p != ".")

def extract_metadata(code: str) -> Tuple[str, str, str]:
    tag_match = TAG_PATTERN.search(code)
    
    if tag_match:
        tag_type = tag_match.group("tag").lower()
        custom_name = tag_match.group("n") or ""
        
        if tag_type == "project":
            return "data", custom_name, custom_name
        
        return tag_type, custom_name, ""
    
    try:
        tree = ast.parse(code)
        docstring = ast.get_docstring(tree)
        if docstring:
            role = docstring.strip().splitlines()[0]
            return "data", "", role
    except:
        pass
    
    return "data", "", "Module"

# ============================================================================
# GRAPH BUILDER
# ============================================================================

class DependencyGraphBuilder:
    def __init__(self, files: Dict[str, str], folder_structure: Dict, symbol_level: bool = False):
        self.files = files
        self.folder_structure = folder_structure
        self.symbol_level = symbol_level
        self.nodes: List[GraphNode] = []
        self.edges: Set[Tuple[str, str, str]] = set()
        self.module_map: Dict[str, str] = {}
        self.external_deps: Set[str] = set()
        self.module_details: Dict[str, Dict] = {}
        self.layout_depth: Dict[str, int] = {}
        self.complexity_calculated = 0
        self.complexity_failed = 0
        self.import_resolution_stats = {
            "exact": 0, "fuzzy": 0, "basename": 0, "top_level": 0, "failed": 0
        }
    
    def build(self) -> Dict:
        self._detect_project_roots()
        logger.info(f"Detected roots: {self.roots}")
        logger.info(f"Module map has {len(self.module_map)} entries")
        
        log_memory_usage()
        
        self._analyze_modules()
        self._add_external_nodes()
        self._calculate_layout()
        
        logger.info(
            f"Built graph: {len(self.nodes)} nodes, {len(self.edges)} edges, "
            f"{self.complexity_calculated} complexity calculations"
        )
        
        log_memory_usage()
        
        return {
            "version": "4.9-optimized",
            "generatedAt": datetime.now().isoformat(),
            "nodes": [asdict(n) for n in self.nodes],
            "edges": [{"from": a, "to": b, "type": t} for a, b, t in sorted(self.edges)],
            "module_details": self.module_details,
            "folder_structure": self.folder_structure,
            "file_contents": self.files,
            "layout_depth": self.layout_depth,
            "metadata": {
                "total_files": len(self.files),
                "total_modules": sum(1 for n in self.nodes if n.kind == "module"),
                "total_symbols": sum(1 for n in self.nodes if n.kind in ["class", "function"]),
                "total_external": sum(1 for n in self.nodes if n.kind == "external"),
                "total_edges": len(self.edges),
                "symbol_level": self.symbol_level,
                "radon_available": RADON_AVAILABLE,
                "file_contents_included": True,
                "memory_optimized": True
            }
        }
    
    def _detect_project_roots(self):
        dirs = sorted(set(posixpath.dirname(p) for p in self.files.keys()))
        candidates = set()
        
        for d in dirs:
            top = d.split("/")[0] if "/" in d else d
            if top in {"src", "python", "lib", "pkg", "app"}:
                candidates.add(top)
        
        if not candidates:
            candidates = {p.split("/")[0] for p in self.files.keys() if "/" in p} or {""}
        
        self.roots = sorted(candidates)
        
        for filepath in self.files.keys():
            for root in self.roots:
                if filepath.startswith(root):
                    mod_id = module_key_from_path(root, filepath)
                    self.module_map[mod_id] = filepath
                    break
    
    def _resolve_import(self, import_name: str) -> Optional[str]:
        if import_name in self.module_map:
            self.import_resolution_stats["exact"] += 1
            return import_name
        
        for key in self.module_map:
            if key.endswith('.' + import_name):
                self.import_resolution_stats["fuzzy"] += 1
                return key
        
        import_basename = import_name.split('.')[-1]
        for key in self.module_map:
            if key.split('.')[-1] == import_basename:
                self.import_resolution_stats["basename"] += 1
                return key
        
        for key in self.module_map:
            if import_name in key:
                self.import_resolution_stats["fuzzy"] += 1
                return key
        
        top = get_top_module(import_name)
        if top in self.module_map:
            self.import_resolution_stats["top_level"] += 1
            return top
        
        self.import_resolution_stats["failed"] += 1
        return None
    
    def _analyze_modules(self):
        total = len(self.module_map)
        processed = 0
        
        for module_id, filepath in self.module_map.items():
            code = self.files[filepath]
            
            try:
                tree = ast.parse(code)
            except SyntaxError:
                self.complexity_failed += 1
                continue
            
            complexity, blocks = calculate_module_complexity(code, module_id)
            if complexity.block_count > 0 or complexity.max_complexity > 0:
                self.complexity_calculated += 1
            else:
                self.complexity_failed += 1
            
            mod_type, title, role = extract_metadata(code)
            if not title:
                title = module_id.split(".")[-1]
            if not role:
                role = "Module"
            
            parent_pkg = ".".join(module_id.split(".")[:-1])
            visitor = ImportVisitor(parent_pkg)
            visitor.visit(tree)
            
            call_visitor = CallGraphVisitor()
            call_visitor.visit(tree)
            
            entry_visitor = EntrypointVisitor()
            entry_visitor.visit(tree)
            
            symbols = extract_symbols(tree)
            symbol_complexities = map_symbol_complexities(blocks)
            
            functions = []
            for sym_name, sym_kind, sym_doc, lineno in symbols:
                if sym_kind == "function":
                    complexity_val = symbol_complexities.get(sym_name, 0)
                    functions.append(FunctionDetails(
                        name=sym_name,
                        docstring=sym_doc,
                        lineno=lineno,
                        complexity=complexity_val,
                        calls=list(call_visitor.calls.get(sym_name, [])),
                        is_entrypoint=sym_name in entry_visitor.entrypoints
                    ))
            
            called_by = defaultdict(list)
            for f, targets in call_visitor.calls.items():
                for t in targets:
                    called_by[t].append(f)
            for func in functions:
                func.called_by = called_by.get(func.name, [])
            
            all_called = set(c for targets in call_visitor.calls.values() for c in targets)
            dead = [f.name for f in functions if f.name not in all_called and not f.is_entrypoint]
            
            stats = NodeStats(
                lines=code.count('\n') + 1,
                classes=sum(1 for _, k, _, _ in symbols if k == "class"),
                functions=sum(1 for _, k, _, _ in symbols if k == "function"),
                imports=len(visitor.imports),
                complexity=complexity
            )
            
            node = GraphNode(
                id=module_id,
                kind="module",
                type=mod_type,
                title=title,
                path=filepath,
                icon=TYPE_ICONS.get(mod_type, "💾"),
                content=role,
                project=get_top_module(module_id),
                stats=stats.to_dict()
            )
            self.nodes.append(node)
            
            self.module_details[module_id] = {
                "path": filepath,
                "type": mod_type,
                "role": role,
                "imports": visitor.imports,
                "symbols": len(symbols),
                "stats": stats.to_dict(),
                "functions": [asdict(f) for f in functions],
                "entrypoints": list(entry_visitor.entrypoints),
                "call_graph": {k: list(v) for k, v in call_visitor.calls.items()},
                "dead_functions": dead
            }
            
            for imp in visitor.imports:
                target = self._resolve_import(imp)
                top_level = get_top_module(imp)
                
                if target and target != module_id:
                    self.edges.add((module_id, target, "imports"))
                elif not is_stdlib(top_level):
                    self.external_deps.add(top_level)
            
            for call_alias in visitor.calls:
                for imp in visitor.imports:
                    if call_alias == imp.split(".")[-1]:
                        target = self._resolve_import(imp)
                        if target and target != module_id:
                            self.edges.add((module_id, target, "calls"))
                            break
            
            if self.symbol_level and blocks:
                for sym_name, sym_kind, sym_doc, lineno in symbols:
                    sym_id = f"{module_id}.{sym_name}"
                    sym_complexity_value = symbol_complexities.get(sym_name, 0)
                    
                    if sym_complexity_value > 0:
                        sym_complexity = ComplexityMetrics(
                            max_complexity=sym_complexity_value,
                            avg_complexity=float(sym_complexity_value),
                            maintainability_index=complexity.maintainability_index,
                            block_count=1,
                            high_complexity_blocks=1 if sym_complexity_value > 10 else 0
                        )
                    else:
                        sym_complexity = None
                    
                    sym_stats = NodeStats(lines=0, complexity=sym_complexity)
                    
                    sym_node = GraphNode(
                        id=sym_id,
                        kind=sym_kind,
                        type=mod_type,
                        title=sym_name,
                        path=filepath,
                        icon=TYPE_ICONS.get(sym_kind, "⚙️"),
                        content=sym_doc.splitlines()[0] if sym_doc else sym_name,
                        project=get_top_module(module_id),
                        stats=sym_stats.to_dict(),
                        parent=module_id
                    )
                    self.nodes.append(sym_node)
                    self.edges.add((module_id, sym_id, "defines"))
            
            processed += 1
            if processed % 500 == 0:
                gc.collect()
                mem_mb = log_memory_usage()
                logger.info(f"Progress: {processed}/{total} modules processed")
                
                if mem_mb > MEMORY_WARNING_THRESHOLD:
                    logger.warning(f"⚠️ Memory usage high: {mem_mb:.1f} MB")
    
    def _add_external_nodes(self):
        for ext_pkg in sorted(self.external_deps):
            ext_node = GraphNode(
                id=f"external:{ext_pkg}",
                kind="external",
                type="external",
                title=ext_pkg,
                path=f"external/{ext_pkg}",
                icon=TYPE_ICONS["external"],
                content=f"External package: {ext_pkg}",
                project="external",
                stats={"Type": "External Package"}
            )
            self.nodes.append(ext_node)
            
            for module_id, details in self.module_details.items():
                for imp in details["imports"]:
                    if get_top_module(imp) == ext_pkg:
                        self.edges.add((module_id, f"external:{ext_pkg}", "external"))
                        break
    
    def _calculate_layout(self):
        if not self.edges:
            angle = 0
            step = 360 / max(1, len(self.nodes))
            radius = 500
            
            for node in self.nodes:
                node.x = radius * math.cos(math.radians(angle))
                node.y = radius * math.sin(math.radians(angle))
                angle += step
            return
        
        graph = defaultdict(set)
        reverse_graph = defaultdict(set)
        all_nodes = set(n.id for n in self.nodes if n.kind in ["module", "external"])
        
        for src, dst, edge_type in self.edges:
            if edge_type in ["imports", "calls", "external"]:
                if src in all_nodes and dst in all_nodes:
                    graph[src].add(dst)
                    reverse_graph[dst].add(src)
        
        visited = set()
        order = []
        
        def dfs1(node):
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs1(neighbor)
            order.append(node)
        
        for node in all_nodes:
            if node not in visited:
                dfs1(node)
        
        component = {}
        comp_id = 0
        visited.clear()
        
        def dfs2(node, cid):
            component[node] = cid
            visited.add(node)
            for neighbor in reverse_graph[node]:
                if neighbor not in visited:
                    dfs2(neighbor, cid)
        
        for node in reversed(order):
            if node not in visited:
                dfs2(node, comp_id)
                comp_id += 1
        
        comp_graph = defaultdict(set)
        for src, dst, _ in self.edges:
            if src in component and dst in component:
                if component[src] != component[dst]:
                    comp_graph[component[src]].add(component[dst])
        
        comp_depth = {i: 0 for i in range(comp_id)}
        in_degree = defaultdict(int)
        
        for src in comp_graph:
            for dst in comp_graph[src]:
                in_degree[dst] += 1
        
        queue = deque([c for c in range(comp_id) if in_degree[c] == 0])
        
        while queue:
            c = queue.popleft()
            for neighbor in comp_graph[c]:
                comp_depth[neighbor] = max(comp_depth[neighbor], comp_depth[c] + 1)
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        depth_nodes = defaultdict(list)
        
        for node in self.nodes:
            if node.kind in ["module", "external"]:
                depth = comp_depth.get(component.get(node.id, 0), 0)
                depth_nodes[depth].append(node)
                self.layout_depth[node.id] = depth
            elif node.parent:
                parent_depth = comp_depth.get(component.get(node.parent, 0), 0)
                depth_nodes[parent_depth].append(node)
                self.layout_depth[node.id] = parent_depth
        
        for depth, nodes_at_depth in depth_nodes.items():
            radius = 300 + depth * 200
            angle_step = 360 / max(1, len(nodes_at_depth))
            
            for i, node in enumerate(nodes_at_depth):
                angle = i * angle_step
                node.x = radius * math.cos(math.radians(angle))
                node.y = radius * math.sin(math.radians(angle))

# ============================================================================
# FILE HANDLING
# ============================================================================

def extract_python_files(zip_bytes: bytes) -> Tuple[Dict[str, str], Dict]:
    try:
        zf = ZipFile(io.BytesIO(zip_bytes))
    except Exception as e:
        raise HTTPException(400, f"Invalid ZIP: {e}")
    
    if len(zf.namelist()) > MAX_FILES:
        raise HTTPException(400, f"Too many files (max {MAX_FILES})")
    
    files = {}
    folder_structure = {"name": "root", "type": "folder", "children": {}, "files": []}
    skipped = 0
    skipped_dirs = set()
    
    for name in zf.namelist():
        if name.startswith("__MACOSX") or "__pycache__" in name:
            continue
        
        name = name.replace("\\", "/")
        
        if should_skip_directory(name):
            dir_name = name.split('/')[0] if '/' in name else name
            skipped_dirs.add(dir_name)
            skipped += 1
            continue
        
        if name.endswith("/"):
            parts = [p for p in name.rstrip("/").split("/") if p]
            current = folder_structure
            for part in parts:
                if part not in current["children"]:
                    current["children"][part] = {
                        "name": part,
                        "type": "folder",
                        "children": {},
                        "files": []
                    }
                current = current["children"][part]
        
        elif name.endswith(".py"):
            try:
                content = zf.read(name).decode("utf-8", errors="ignore")
                
                if len(content) > MAX_SINGLE_FILE_SIZE:
                    logger.warning(f"Skipping {name}: too large ({len(content)} bytes)")
                    skipped += 1
                    continue
                
                files[name] = content
                
                parts = name.split("/")
                current = folder_structure
                
                for part in parts[:-1]:
                    if part not in current["children"]:
                        current["children"][part] = {
                            "name": part,
                            "type": "folder",
                            "children": {},
                            "files": []
                        }
                    current = current["children"][part]
                
                current["files"].append({
                    "name": parts[-1],
                    "path": name,
                    "size": len(content)
                })
                
            except Exception as e:
                logger.warning(f"Could not read {name}: {e}")
    
    if skipped > 0:
        logger.info(f"📊 Skipped {skipped} files from: {', '.join(sorted(skipped_dirs))}")
    
    return files, folder_structure

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="DNAiOS Architecture Analyzer - Optimized",
    version="4.9-optimized",
    description="4GB max upload with memory monitoring"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    mem_mb = log_memory_usage() if PSUTIL_AVAILABLE else 0
    
    return {
        "service": "DNAiOS Architecture Analyzer",
        "version": "4.9-optimized",
        "status": "operational",
        "features": [
            "✅ Monaco Editor support",
            "✅ 4GB max upload (optimized for 16GB RAM)",
            "✅ Auto-skip venv/node_modules",
            "✅ Memory monitoring",
            "✅ Progress logging",
            "✅ Dead code detection",
            "✅ Complexity metrics"
        ],
        "configuration": {
            "max_zip_size": f"{MAX_ZIP_SIZE / 1024 / 1024 / 1024:.1f} GB",
            "max_single_file": f"{MAX_SINGLE_FILE_SIZE / 1024 / 1024} MB",
            "max_files": MAX_FILES,
            "memory_threshold": f"{MEMORY_WARNING_THRESHOLD / 1024:.1f} GB"
        },
        "radon_status": "available" if RADON_AVAILABLE else "not_installed",
        "psutil_status": "available" if PSUTIL_AVAILABLE else "not_installed",
        "current_memory_mb": f"{mem_mb:.1f}" if mem_mb > 0 else "unavailable"
    }

@app.post("/analyze")
async def analyze(
    zipfile: UploadFile = File(None),
    pyfile: UploadFile = File(None),
    symbol_level: bool = Form(False)
):
    """Analyze Python project with memory optimization"""
    try:
        logger.info("=" * 80)
        logger.info("Starting analysis...")
        log_memory_usage()
        
        files = {}
        folder_structure = {"name": "root", "type": "folder", "children": {}, "files": []}
        
        if pyfile and pyfile.filename.endswith('.py'):
            content = await pyfile.read()
            if len(content) > MAX_SINGLE_FILE_SIZE:
                raise HTTPException(400, f"File too large (max {MAX_SINGLE_FILE_SIZE / 1024 / 1024} MB)")
            files[pyfile.filename] = content.decode("utf-8", errors="ignore")
            folder_structure["files"].append({
                "name": pyfile.filename,
                "path": pyfile.filename,
                "size": len(content)
            })
            logger.info(f"📄 Loaded single file: {pyfile.filename}")
        
        elif zipfile:
            zip_data = await zipfile.read()
            zip_size_mb = len(zip_data) / 1024 / 1024
            logger.info(f"📦 ZIP file size: {zip_size_mb:.2f} MB")
            
            if len(zip_data) > MAX_ZIP_SIZE:
                raise HTTPException(400, f"ZIP too large (max {MAX_ZIP_SIZE / 1024 / 1024 / 1024:.1f} GB)")
            
            log_memory_usage()
            files, folder_structure = extract_python_files(zip_data)
            
            del zip_data
            gc.collect()
            log_memory_usage()
        
        else:
            raise HTTPException(400, "Provide zipfile or pyfile")
        
        if not files:
            return {
                "version": "4.9-optimized",
                "nodes": [],
                "edges": [],
                "folder_structure": folder_structure,
                "file_contents": {},
                "metadata": {"message": "No Python files found"}
            }
        
        logger.info(f"📊 Processing {len(files)} Python files...")
        log_memory_usage()
        
        builder = DependencyGraphBuilder(files, folder_structure, symbol_level)
        result = builder.build()
        
        logger.info(f"✅ Analysis complete!")
        logger.info(f"📈 Results: {len(result['nodes'])} nodes, {len(result['edges'])} edges")
        log_memory_usage()
        logger.info("=" * 80)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}", exc_info=True)
        raise HTTPException(500, f"Error: {e}")
    finally:
        gc.collect()

@app.get("/health")
async def health():
    mem_mb = log_memory_usage() if PSUTIL_AVAILABLE else 0
    
    return {
        "status": "healthy",
        "version": "4.9-optimized",
        "radon": RADON_AVAILABLE,
        "psutil": PSUTIL_AVAILABLE,
        "file_contents_support": True,
        "memory_monitoring": PSUTIL_AVAILABLE,
        "current_memory_mb": f"{mem_mb:.1f}" if mem_mb > 0 else "unavailable",
        "limits": {
            "max_zip_gb": MAX_ZIP_SIZE / 1024 / 1024 / 1024,
            "max_single_file_mb": MAX_SINGLE_FILE_SIZE / 1024 / 1024,
            "max_files": MAX_FILES
        }
    }

@app.get("/memory")
async def memory_status():
    """Get current memory usage statistics"""
    if not PSUTIL_AVAILABLE:
        return {"error": "psutil not installed", "install": "pip install psutil"}
    
    try:
        process = psutil.Process()
        mem_info = process.memory_info()
        
        virtual_mem = psutil.virtual_memory()
        
        return {
            "process": {
                "rss_mb": mem_info.rss / 1024 / 1024,
                "vms_mb": mem_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            },
            "system": {
                "total_gb": virtual_mem.total / 1024 / 1024 / 1024,
                "available_gb": virtual_mem.available / 1024 / 1024 / 1024,
                "used_gb": virtual_mem.used / 1024 / 1024 / 1024,
                "percent": virtual_mem.percent
            },
            "threshold": {
                "warning_mb": MEMORY_WARNING_THRESHOLD,
                "warning_gb": MEMORY_WARNING_THRESHOLD / 1024
            }
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import Config
    
    print("\n" + "="*80)
    print("DNAiOS Architecture Analyzer v4.9 - Optimized for 16GB RAM")
    print("="*80)
    print("\nStarting on http://0.0.0.0:5001")
    print("\nOptimizations:")
    print("  ✅ 4 GB maximum upload size")
    print("  ✅ Memory monitoring with safety checks")
    print("  ✅ Auto-skip venv/node_modules/build directories")
    print("  ✅ Progress logging every 500 modules")
    print("  ✅ Aggressive garbage collection")
    print("  ✅ Monaco Editor integration ready")
    print("  ✅ Full Python source code available per module")
    print(f"\nStatus:")
    print(f"  Radon: {'✅ Available' if RADON_AVAILABLE else '⚠️ Not installed (pip install radon)'}")
    print(f"  PSUtil: {'✅ Available' if PSUTIL_AVAILABLE else '⚠️ Not installed (pip install psutil)'}")
    print(f"\nLimits:")
    print(f"  Max ZIP: 4 GB")
    print(f"  Max single file: 50 MB")
    print(f"  Max files: {MAX_FILES:,}")
    print(f"  Memory warning: 14 GB")
    print("="*80 + "\n")
    
    if PSUTIL_AVAILABLE:
        log_memory_usage()
    
    # Configure uvicorn with proper settings
    config = Config(
        app=app,
        host="0.0.0.0",
        port=5001,
        timeout_keep_alive=600,  # 10 minutes for large uploads
        limit_concurrency=10,
        limit_max_requests=1000,
        backlog=2048
    )
    
    server = uvicorn.Server(config)
    server.run()