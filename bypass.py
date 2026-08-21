#!/usr/bin/env python3
"""
bypass.py — Auto-Bypass pour Faizimods
• Détecte automatiquement la clé générée par le HWID
• Installe l'intercepteur dans site-packages
• Lance faizimods avec accès accordé
"""

import os
import sys
import subprocess
import re

# ── Chemins ──────────────────────────────────────────────────────────────────
TOOL_DIR  = os.path.dirname(os.path.abspath(__file__))
BINARY    = os.path.join(TOOL_DIR, "faizimods")
USR_FILE  = os.path.join(TOOL_DIR, ".username")
SITE_PY   = "/data/data/com.termux/files/usr/lib/python3.14/site-packages/sitecustomize.py"

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_username():
    if os.path.exists(USR_FILE):
        return open(USR_FILE).read().strip().upper()
    return "YARBASH"

def detect_key(username):
    """Lance le binaire silencieusement pour capturer la clé générée."""
    print(f"  [~] Détection de la clé pour '{username}'...")
    try:
        proc = subprocess.run(
            [BINARY],
            input=b"0\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=35
        )
        out = proc.stdout.decode("utf-8", errors="replace")
        # Pattern : KEY  › USERNAME-AABBCC-DDEEFF-112233
        pat = rf'KEY\s*[›>]\s*({re.escape(username)}-[A-F0-9]{{6}}-[A-F0-9]{{6}}-[A-F0-9]{{6}})'
        m = re.search(pat, out, re.IGNORECASE)
        if m:
            return m.group(1).upper()
    except subprocess.TimeoutExpired:
        print("  [!] Timeout — binary trop lent")
    except Exception as e:
        print(f"  [!] Erreur: {e}")
    return None

def install_interceptor(key):
    """Écrit sitecustomize.py dans site-packages avec la clé injectée."""
    content = f'''\
# sitecustomize.py — Bypass Faizimods (auto-généré)
# Clé: {key}

_KEY = "{key}"

def _is_keys_url(u):
    u = str(u).lower()
    return "keys" in u and ("github" in u or "raw" in u or "githubusercontent" in u)

def _inject(text):
    lines = text.strip().splitlines()
    if _KEY not in lines:
        lines.append(_KEY)
    return "\\n".join(lines) + "\\n"

class _FR:
    def __init__(self, orig):
        self.status_code = 200
        self.headers  = getattr(orig, "headers", {{}})
        self.encoding = "utf-8"
        self._t = _inject(orig.text)
    @property
    def text(self): return self._t
    @property
    def content(self): return self._t.encode()
    def json(self): return self._t
    def raise_for_status(self): pass
    def __getattr__(self, n): return None

try:
    import requests as _r
    _rg = _r.get; _rp = _r.post; _rq = _r.request; _rs = _r.Session.request
    _r.get            = lambda u, **kw: (_FR(_rg(u, **kw)) if _is_keys_url(u) else _rg(u, **kw))
    _r.post           = lambda u, **kw: _rp(u, **kw)
    _r.request        = lambda m, u, **kw: (_FR(_rq(m,u,**kw)) if _is_keys_url(u) else _rq(m,u,**kw))
    _r.Session.request = lambda s,m,u,**kw: (_FR(_rs(s,m,u,**kw)) if _is_keys_url(u) else _rs(s,m,u,**kw))
except ImportError:
    pass

try:
    import urllib.request as _u, io as _io
    _uo = _u.urlopen
    class _FU:
        def __init__(self, c): self._c = c.encode(); self.status = 200
        def read(self): return self._c
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def _uo2(url, data=None, **kw):
        us = str(getattr(url, "full_url", url))
        r  = _uo(url, data, **kw)
        c  = r.read().decode("utf-8", errors="replace")
        return _FU(_inject(c)) if _is_keys_url(us) else _io.BytesIO(c.encode())
    _u.urlopen = _uo2
except Exception:
    pass
'''
    with open(SITE_PY, "w") as f:
        f.write(content)
    print(f"  [✓] Intercepteur installé  →  {SITE_PY}")

def main():
    print()
    print("╔══════════════════════════════════════╗")
    print("║   FAIZIMODS AUTO-BYPASS  v1.0        ║")
    print("╚══════════════════════════════════════╝")
    print()

    # 1. Username
    username = get_username()
    print(f"  [i] Username  : {username}")

    # 2. Détecter la clé
    key = detect_key(username)

    if not key:
        print("  [!] Clé non détectée — utilisation de la dernière clé connue")
        # Lire la clé depuis sitecustomize.py existant
        try:
            with open(SITE_PY) as f:
                m = re.search(r'_KEY\s*=\s*"([^"]+)"', f.read())
                if m:
                    key = m.group(1)
                    print(f"  [~] Clé récupérée depuis le cache: {key}")
        except Exception:
            pass

    if not key:
        print("  [✗] Impossible de détecter la clé. Arrêt.")
        sys.exit(1)

    print(f"  [i] Clé cible : {key}")

    # 3. Installer l'intercepteur
    install_interceptor(key)

    # 4. Lancer faizimods (remplace le processus actuel)
    print(f"\n  [→] Lancement de faizimods...\n")
    os.execv(BINARY, [BINARY])

if __name__ == "__main__":
    main()
