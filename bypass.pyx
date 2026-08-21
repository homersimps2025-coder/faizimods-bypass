# bypass.pyx — Version Cython de bypass.py
# Compile avec : python3 setup_bypass.py build_ext --inplace
# cython: language_level=3

import os
import sys
import subprocess
import re

cdef str TOOL_DIR  = os.path.dirname(os.path.abspath(__file__))
cdef str BINARY    = os.path.join(TOOL_DIR, "faizimods")
cdef str USR_FILE  = os.path.join(TOOL_DIR, ".username")
cdef str SITE_PY   = "/data/data/com.termux/files/usr/lib/python3.14/site-packages/sitecustomize.py"

cpdef str get_username():
    if os.path.exists(USR_FILE):
        return open(USR_FILE).read().strip().upper()
    return "YARBASH"

cpdef str detect_key(str username):
    """Lance le binaire silencieusement et capture la clé générée."""
    print(f"  [~] Détection clé pour '{username}'...")
    cdef str out
    cdef object proc
    try:
        proc = subprocess.run(
            [BINARY],
            input=b"0\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=35
        )
        out = proc.stdout.decode("utf-8", errors="replace")
        pat = rf'KEY\s*[›>]\s*({re.escape(username)}-[A-F0-9]{{6}}-[A-F0-9]{{6}}-[A-F0-9]{{6}})'
        m = re.search(pat, out, re.IGNORECASE)
        if m:
            return m.group(1).upper()
    except subprocess.TimeoutExpired:
        print("  [!] Timeout")
    except Exception as e:
        print(f"  [!] Erreur: {e}")
    return None

cpdef void install_interceptor(str key):
    """Installe sitecustomize.py dans site-packages avec la clé."""
    content = f'''\
# sitecustomize.py — Bypass Faizimods (auto-généré par bypass.pyx)
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
    _r.get             = lambda u,**kw: (_FR(_rg(u,**kw)) if _is_keys_url(u) else _rg(u,**kw))
    _r.post            = lambda u,**kw: _rp(u,**kw)
    _r.request         = lambda m,u,**kw: (_FR(_rq(m,u,**kw)) if _is_keys_url(u) else _rq(m,u,**kw))
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
        us = str(getattr(url,"full_url",url))
        r = _uo(url, data, **kw)
        c = r.read().decode("utf-8", errors="replace")
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
    print("║   FAIZIMODS AUTO-BYPASS  v1.0 (pyx)  ║")
    print("╚══════════════════════════════════════╝")
    print()

    cdef str username = get_username()
    cdef str key
    print(f"  [i] Username  : {username}")

    key = detect_key(username)

    if not key:
        print("  [!] Clé non détectée — lecture du cache...")
        try:
            with open(SITE_PY) as f:
                m = re.search(r'_KEY\s*=\s*"([^"]+)"', f.read())
                if m:
                    key = m.group(1)
                    print(f"  [~] Cache: {key}")
        except Exception:
            pass

    if not key:
        print("  [✗] Clé introuvable. Arrêt.")
        sys.exit(1)

    print(f"  [i] Clé cible : {key}")
    install_interceptor(key)
    print(f"\n  [→] Lancement...\n")
    os.execv(BINARY, [BINARY])

if __name__ == "__main__":
    main()
