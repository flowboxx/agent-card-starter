#!/usr/bin/env python3
"""Thin wrapper kept for the old path. The example server lives in agent_card/mcp_server.py
and ships with the package (command: agent-card-server). Dünne Hülle, Code liegt im Paket."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from agent_card.mcp_server import *  # noqa: E402,F401,F403
from agent_card.mcp_server import main  # noqa: E402

if __name__ == "__main__":
    main()
