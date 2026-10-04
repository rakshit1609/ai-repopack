# 📦 AI-Repopack

**Pack any repository into clean, security-sanitized context for Claude, ChatGPT, and Cursor.**

---

## ⚡ Features

- **Automated PII & Secret Redaction**: Automatically scrubs API keys, auth tokens, AWS credentials, and `.env` values before sending to LLMs.
- **Token Estimation**: Built-in accurate OpenAI/Anthropic token counting.
- **Smart Filtering**: Automatically ignores lockfiles, images, binaries, caches, and build artifacts.
- **XML / Markdown Context Structure**: Industry-standard `<repository>` hierarchy with CDATA blocks to prevent prompt injection.

---

## 🚀 Usage

```bash
pip install .
repopack . -o codebase.xml
```
