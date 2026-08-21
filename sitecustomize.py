# sitecustomize.py — Bypass Faizimods (auto-généré par bypass.pyx)
_KEY = "YARBASH-64C92D-29654C-7E33D0"
def _is_keys_url(u):
    u = str(u).lower()
    return "keys" in u and ("github" in u or "raw" in u or "githubusercontent" in u)
def _inject(text):
    lines = text.strip().splitlines()
    if _KEY not in lines:
        lines.append(_KEY)
    return "\n".join(lines) + "\n"
class _FR:
    def __init__(self, orig):
        self.status_code = 200
        self.headers  = getattr(orig, "headers", {})
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
