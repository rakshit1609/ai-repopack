import os
import re
import fnmatch
from pathlib import Path
from typing import List, Dict, Tuple, Set

DEFAULT_IGNORE = {
    ".git", ".svn", ".hg", "__pycache__", "node_modules", "dist", "build", ".venv", "venv",
    ".idea", ".vscode", ".DS_Store", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.exe", "*.bin", "*.png",
    "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg", "*.ico", "*.pdf", "*.zip", "*.tar",
    "*.gz", "*.mp4", "*.mp3", "*.wav", ".env", ".env.*", "*.pem", "*.key", "id_rsa"
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|auth|bearer)\s*[:=]\s*['\"]([^'\"]{8,})['\"]"),
    re.compile(r"(?i)ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"(?i)sk-[a-zA-Z0-9]{32,}"),
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
]

def sanitize_content(text: str) -> str:
    text = SECRET_PATTERNS[0].sub(lambda m: f"{m.group(1)} = '[REDACTED_SECRET]'", text)
    for pat in SECRET_PATTERNS[1:]:
        text = pat.sub("[REDACTED_SECRET]", text)
    return text

def should_ignore(path: Path, root: Path, custom_ignores: Set[str]) -> bool:
    rel_path = path.relative_to(root).as_posix()
    for part in path.relative_to(root).parts:
        if part in DEFAULT_IGNORE or part in custom_ignores:
            return True
    for pattern in list(DEFAULT_IGNORE) + list(custom_ignores):
        if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(rel_path, pattern):
            return True
    return False

def pack_repository(root_dir: str, max_file_size_kb: int = 250, custom_ignores: Set[str] = None) -> Tuple[str, Dict[str, int]]:
    root = Path(root_dir).resolve()
    ignores = custom_ignores or set()
    
    file_tree = []
    packed_files = []
    stats = {"total_files": 0, "packed_files": 0, "skipped_files": 0, "total_chars": 0}
    
    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        if should_ignore(current_dir, root, ignores):
            dirnames[:] = []
            continue
            
        for f in filenames:
            stats["total_files"] += 1
            file_path = current_dir / f
            if should_ignore(file_path, root, ignores):
                stats["skipped_files"] += 1
                continue
                
            rel_path = file_path.relative_to(root).as_posix()
            file_tree.append(rel_path)
            
            try:
                size_kb = file_path.stat().st_size / 1024
                if size_kb > max_file_size_kb:
                    stats["skipped_files"] += 1
                    continue
                    
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                sanitized = sanitize_content(content)
                
                packed_files.append({
                    "path": rel_path,
                    "content": sanitized,
                    "lines": len(sanitized.splitlines())
                })
                stats["packed_files"] += 1
                stats["total_chars"] += len(sanitized)
            except OSError:
                stats["skipped_files"] += 1
                
    output_lines = [
        "<!-- AI CODEBASE CONTEXT CREATED BY AI-REPOPACK -->",
        f"<repository root='{root.name}'>",
        "  <directory_structure>",
    ]
    for ft in sorted(file_tree):
        output_lines.append(f"    <file path='{ft}' />")
    output_lines.append("  </directory_structure>\n  <files>")
    
    for pf in packed_files:
        output_lines.append(f"    <file path='{pf['path']}' lines='{pf['lines']}'>")
        output_lines.append("<![CDATA[")
        output_lines.append(pf["content"])
        output_lines.append("]]>")
        output_lines.append("    </file>")
        
    output_lines.append("  </files>\n</repository>")
    
    full_output = "\n".join(output_lines)
    return full_output, stats
