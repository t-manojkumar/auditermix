# Contributing to auditermix

Thank you for taking the time to contribute! Here's how to get set up.

---

## Dev setup

```bash
git clone https://github.com/t-manojkumar/auditermix
cd auditermix

# With uv (recommended)
uv run auditermix.py

# With plain Python
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
python auditermix.py
```

## Guidelines

- Keep the app as a **single file** (`auditermix.py`) — no additional modules
- All output goes through the `_ln()`, `_rule()`, `_print_warning()`, `_print_error()` helpers
- Never use `print()` for warnings/errors directly in download code
- All colour functions must respect `_TTY` — never raw ANSI in string literals
- No bare `except:` — always catch a specific exception or `Exception`
- Run syntax check before opening a PR:
  ```bash
  python -c "import ast; ast.parse(open('auditermix.py').read())"
  ```

## Adding a noise filter pattern

Add it to `_MUTED` in the noise filter section. If it needs a special one-time hint (like the JS-challenge case), add it to `_JS_RE` and handle it in `SilentLogger.warning()`.

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).
Always include OS, Python version, yt-dlp version, and full terminal output.
