"""Lesson 20 (bonus, after week 15): give ANY AI app your robot, with MCP.

In Lesson 18 the tools (look, go_to, pick_up, put_in_bin) only worked inside our own agent loop.
MCP (the Model Context Protocol) is a standard plug: write the tools ONCE as an MCP server, and any
MCP app (Claude Desktop, Claude Code, and many others) can discover and call them. Like USB for AI tools.

The important idea: the SERVER is the robot's last line of defence. You don't know which AI will connect,
or what it was told. So the rules that must never break live here, in your guard() function.

Setup (once, in your venv, needs Python 3.11+):   pip install mcp
Connect it to Claude Code:     claude mcp add robo-helper -- <path to venv python> <path to this file>
Watch the robot live, in a second terminal:      python3 lesson20_watch.py
Test it without any AI:        python3 lesson20_mcp_server.py --selftest
"""

import sys
from pathlib import Path

from sim import SimRobot, frame_text, CAT
from lesson18_world_class import execute_tool

PROTECTED = {"green block"}   # the owner's favourite block: never pick it up
MAX_CALLS = 40                # a runaway AI gets cut off
LIVE = Path(__file__).resolve().parent / "traces" / "live.txt"


# ---------------- YOUR HOMEWORK: the server's own rules ----------------

def guard(name, args, calls):
    """Decide whether a tool call may run, whoever is asking. Return (True, "") or (False, reason).
      1. if len(calls) >= MAX_CALLS -> (False, "too many calls: ask the person to reset the room")
      2. if name == "pick_up" and args.get("object") is in PROTECTED -> (False, "the <object> is protected: never pick it up")
      3. otherwise (True, "")"""
    # BEGIN SOLUTION
    if len(calls) >= MAX_CALLS:
        return False, "too many calls: ask the person to reset the room"
    if name == "pick_up" and args.get("object") in PROTECTED:
        return False, f"the {args['object']} is protected: never pick it up"
    return True, ""
    # END SOLUTION


# ---------------- provided: the server ----------------

class RobotService:
    """One robot that stays alive between tool calls, plus a log of every call."""

    def __init__(self, cat=True):
        self.reset(cat)

    def reset(self, cat=True):
        self.robot = SimRobot(surprises=(CAT,) if cat else ())
        self.calls = []
        self.show()

    def call(self, name, args):
        """Run one tool call through guard() then Lesson 18's execute_tool(). Returns (ok, text)."""
        ok, reason = guard(name, args, self.calls)
        if ok:
            ok, text = execute_tool(self.robot, name, args, set(self.robot.objects))
        else:
            text = f"Refused by the robot's server: {reason}."
        self.calls.append({"tool": name, "args": args, "ok": ok, "result": text})
        self.show()
        return ok, text

    def show(self):
        LIVE.parent.mkdir(exist_ok=True)
        last = self.calls[-1] if self.calls else None
        note = f"\nlast call: {last['tool']}({last['args']}) -> {'ok' if last['ok'] else 'REFUSED/FAILED'}: {last['result']}" if last else ""
        LIVE.write_text(frame_text(self.robot.frames[-1]) + f"\ncalls: {len(self.calls)}/{MAX_CALLS}" + note + "\n")


def build_server(service):
    from mcp.server import MCPServer   # pip install mcp
    from mcp.server.mcpserver.exceptions import ToolError

    server = MCPServer("robo-helper", instructions=(
        "You control Robo-Helper, a small robot in a simulated room with three blocks and a bin. "
        "Call look first. To bin a block: go_to it, pick_up it, then put_in_bin. "
        "Some actions may be refused by the robot's own safety rules; tell the person when that happens."))

    def run(name, args):
        ok, text = service.call(name, args)
        if not ok:
            raise ToolError(text)   # MCP apps see a failed tool call, with this reason
        return text

    @server.tool()
    def look() -> str:
        """Describe the room: robot position, what it holds, where each block is, what's in the bin, obstacles seen."""
        return run("look", {})

    @server.tool()
    def go_to(object: str) -> str:
        """Drive to a block ("red block", "blue block" or "green block"). Replans around obstacles."""
        return run("go_to", {"object": object})

    @server.tool()
    def pick_up(object: str) -> str:
        """Pick up a block. The robot must already be at the block (use go_to first)."""
        return run("pick_up", {"object": object})

    @server.tool()
    def put_in_bin() -> str:
        """Drive to the bin and drop the block the robot is holding."""
        return run("put_in_bin", {})

    @server.tool()
    def reset_room(cat: bool = True) -> str:
        """Put everything back where it started. cat=True puts the cat back in the way at (4, 1)."""
        service.reset(cat)
        return "Room reset. " + service.robot.look()

    return server


def selftest():
    """Check guard() and the service without any AI or MCP install."""
    s = RobotService()
    for name, args in [("look", {}), ("go_to", {"object": "blue block"}), ("pick_up", {"object": "blue block"}),
                       ("put_in_bin", {}), ("go_to", {"object": "green block"}), ("pick_up", {"object": "green block"}),
                       ("pick_up", {"object": "the cat"})]:
        ok, text = s.call(name, args)
        print(f"{'✓' if ok else '✗'} {name}({args}) -> {text}")
    print("\n" + LIVE.read_text())


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        build_server(RobotService()).run()   # talks MCP over stdin/stdout: don't print() in here!
