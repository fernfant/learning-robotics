"""Lesson 6: finding the way. Breadth-first search, then A*."""

import heapq
from collections import deque

from world import ROOM, ROBOT_START, OBJECTS, find_bin, is_free, render
from lesson01_moving import DIRECTIONS, move, manhattan


def neighbors(room, pos, blocked=()):
    """Free squares one step N/S/E/W from pos, skipping anything in `blocked`.
    Check the directions in the order N, S, E, W."""
    # BEGIN SOLUTION
    out = []
    for d in "NSEW":
        p = move(pos, d)
        if is_free(room, p) and p not in blocked:
            out.append(p)
    return out
    # END SOLUTION


def bfs_path(room, start, goal, blocked=()):
    """Breadth-first search: explore squares in rings of distance 1, 2, 3 ...
    Use a queue (deque), and a dict `came_from` mapping each square to the square we reached it from.
    Return the list of squares from start to goal (both included), or None if unreachable."""
    # BEGIN SOLUTION
    queue = deque([start])
    came_from = {start: None}
    while queue:
        cur = queue.popleft()
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            return path[::-1]
        for nxt in neighbors(room, cur, blocked):
            if nxt not in came_from:
                came_from[nxt] = cur
                queue.append(nxt)
    return None
    # END SOLUTION


def astar_path(room, start, goal, blocked=()):
    """A*: like BFS, but always expand the square with the smallest
    (steps so far + manhattan distance to goal). Use heapq as a priority queue.
    Return (path, expanded), where expanded = how many squares you took off the queue."""
    # BEGIN SOLUTION
    frontier = [(manhattan(start, goal), 0, start)]
    came_from = {start: None}
    cost = {start: 0}
    expanded = 0
    while frontier:
        _, g, cur = heapq.heappop(frontier)
        if g > cost[cur]:
            continue
        expanded += 1
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            return path[::-1], expanded
        for nxt in neighbors(room, cur, blocked):
            ng = g + 1
            if ng < cost.get(nxt, float("inf")):
                cost[nxt] = ng
                came_from[nxt] = cur
                heapq.heappush(frontier, (ng + manhattan(nxt, goal), ng, nxt))
    return None, expanded
    # END SOLUTION


def path_to_commands(path):
    """Turn a path of squares into a command string like "EESW"."""
    # BEGIN SOLUTION
    names = {v: k for k, v in DIRECTIONS.items()}
    return "".join(names[(b[0] - a[0], b[1] - a[1])] for a, b in zip(path, path[1:]))
    # END SOLUTION


if __name__ == "__main__":
    goal = find_bin(ROOM)
    path = bfs_path(ROOM, ROBOT_START, goal)
    print(render(ROOM, ROBOT_START, OBJECTS, path))
    print("BFS steps:", len(path) - 1, "| commands:", path_to_commands(path))
    apath, expanded = astar_path(ROOM, ROBOT_START, goal)
    print("A* steps:", len(apath) - 1, "| squares expanded:", expanded)
