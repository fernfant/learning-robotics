"""Watch the MCP robot live. Run this in a second terminal while an AI app drives the robot (Lesson 20)."""

import time

from lesson20_mcp_server import LIVE

last = None
print("Waiting for the robot... (Ctrl+C to stop)")
while True:
    text = LIVE.read_text() if LIVE.exists() else None
    if text and text != last:
        print("\033[2J\033[H" + text, flush=True)
        last = text
    time.sleep(0.2)
