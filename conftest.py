import sys
from pathlib import Path

# Ensure repository root is on sys.path so tests can import `src` packages
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Add project subdirectories that contain a `src` folder so tests that import
# `src.*` can find the package (e.g., `03_ai_ml_governance/src`). We insert
# each parent directory of a discovered `src` into `sys.path`.
for src_path in REPO_ROOT.rglob('src'):
    parent_dir = str(src_path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
