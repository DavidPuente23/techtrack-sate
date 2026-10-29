"""Inserta el token CSRF en los formularios POST de las plantillas."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
HIDDEN = '<input type="hidden" name="_csrf_token" value="{{ csrf_token }}">'

FORM_RE = re.compile(r'(<form\b[^>]*method=["\']POST["\'][^>]*>)', re.IGNORECASE)

changed = []
for path in TEMPLATES.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    if "_csrf_token" in text:
        continue

    def repl(match):
        return f"{match.group(1)}\n            {HIDDEN}"

    new_text, count = FORM_RE.subn(repl, text)
    if count:
        path.write_text(new_text, encoding="utf-8")
        changed.append(f"{path.relative_to(ROOT)} ({count})")

print("Plantillas actualizadas:")
for item in changed:
    print(" -", item)
if not changed:
    print(" (ninguna)")
