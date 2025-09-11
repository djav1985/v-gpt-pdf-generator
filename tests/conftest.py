import os
import sys
import types
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

weasyprint_stub = types.ModuleType("weasyprint")


class HTML:
    def __init__(self, string):
        self.string = string

    def write_pdf(self, target):
        Path(target).write_bytes(b"")


weasyprint_stub.HTML = HTML

sys.modules.setdefault("weasyprint", weasyprint_stub)

os.environ.setdefault("ROOT_PATH", "")
