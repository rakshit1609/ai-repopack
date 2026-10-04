import argparse
import sys
from pathlib import Path
from .core import pack_repository

def estimate_tokens(text: str) -> int:
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4

def main():
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="AI-Repopack: Pack codebases into clean, sanitized LLM context.")
    parser.add_argument("path", nargs="?", default=".", help="Target repository directory (default: current dir)")
    parser.add_argument("-o", "--output", default="repopack_output.xml", help="Output destination file")
    parser.add_argument("--max-size", type=int, default=250, help="Max file size in KB to include (default: 250)")
    parser.add_argument("--ignore", nargs="*", default=[], help="Additional glob ignore patterns")
    
    args = parser.parse_args()
    
    print(f"📦 AI-Repopack: Scanning repository at '{args.path}'...")
    output_text, stats = pack_repository(args.path, max_file_size_kb=args.max_size, custom_ignores=set(args.ignore))
    
    tokens = estimate_tokens(output_text)
    
    out_file = Path(args.output)
    out_file.write_text(output_text, encoding="utf-8")
    
    print(f"✅ Codebase successfully packed!")
    print(f"  • Files packed:   {stats['packed_files']} / {stats['total_files']} files")
    print(f"  • Estimated tokens: ~{tokens:,} tokens")
    print(f"  • Destination:    {out_file.resolve()}")
    print(f"  • Secrets:        Automatically Redacted & Sanitized")

if __name__ == "__main__":
    main()
