# ai-repopack

Pack a repository into one XML file for pasting into an LLM, with basic secret redaction.

```bash
pip install ai-repopack            # token count is estimated as chars/4
pip install "ai-repopack[tokens]"  # exact counts via tiktoken
repopack . -o codebase.xml
repopack ./src --max-size 100 --ignore "*.test.js"
```

## What it does
- Walks the repo, skips `.git`, `node_modules`, lockfiles, images/binaries, and files over `--max-size` KB (default 250)
- **Skips `.env`, `.env.*`, `*.pem`, `*.key` and `id_rsa` entirely**
- Redacts `api_key|secret|token|password|auth|bearer = "..."` assignments, `ghp_...`, `sk-...` and `AKIA...` keys inside other files
- Wraps each file in `<![CDATA[ ]]>` under a `<repository>` tree

## Limitations (v1)
- Redaction is **regex-based and best-effort**: it will miss secrets in unusual formats. Review output before sharing.
- Does not honour `.gitignore` yet (own ignore list + `--ignore` globs)
- Token count is an estimate unless `tiktoken` is installed

MIT licensed.
