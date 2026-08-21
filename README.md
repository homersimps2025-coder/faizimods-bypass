# faizimods-bypass

Auto-bypass pour **Faizimods Tool** — intercepte la vérification de licence via GitHub et injecte la clé HWID générée automatiquement.

## Installation rapide

```bash
git clone https://github.com/homersimps2025-coder/faizimods-bypass
cd ~/fb-cloning
cp ~/faizimods-bypass/sitecustomize.py /data/data/com.termux/files/usr/lib/python3.14/site-packages/
python3 ~/faizimods-bypass/bypass.py
```

## Compiler la version Cython (optionnel)
```bash
pip install cython setuptools
python3 setup_bypass.py build_ext --inplace
python3 -c "import bypass; bypass.main()"
```

## Fonctionnement
1. Detecte automatiquement la cle HWID generee par le binaire
2. Installe lintercepteur dans site-packages Python
3. Intercepte le fetch GitHub de keys.txt
4. Injecte la cle dans la reponse → ACCESS GRANTED ✅

