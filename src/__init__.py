import sys

if "pytest" not in sys.modules:
    from .main import init

    init()
