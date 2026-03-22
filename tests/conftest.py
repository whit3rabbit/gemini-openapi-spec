"""Shared fixtures for gemini-openapi-spec tests."""

import sys
from pathlib import Path

# Allow importing scripts as modules.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
