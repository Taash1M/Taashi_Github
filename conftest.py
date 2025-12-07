import sys
from pathlib import Path

# Ensure repository root is on sys.path so tests can import `src` packages
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
