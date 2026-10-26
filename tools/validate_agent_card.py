#!/usr/bin/env python3
"""Thin wrapper kept for the original command: python3 tools/validate_agent_card.py card.json
The code lives in agent_card/validator.py (same checks, also available as the `agent-card validate` command)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_card import validator as _v  # noqa: E402

globals().update({k: getattr(_v, k) for k in dir(_v) if not k.startswith("__")})

if __name__ == "__main__":
    sys.exit(_v.main())
