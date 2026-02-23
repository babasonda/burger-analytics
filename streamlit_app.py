import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_app  = os.path.join(_here, "dashboard", "app.py")

sys.path.insert(0, _here)
os.chdir(_here)

with open(_app, encoding="utf-8") as _fh:
    _src = _fh.read()

exec(compile(_src, _app, "exec"), {"__file__": _app, "__name__": "__main__"})
