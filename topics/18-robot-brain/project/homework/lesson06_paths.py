"""Lesson 6: finding the way. Breadth-first search, then A*."""

import heapq
from collections import deque

from world import ROOM, ROBOT_START, OBJECTS, find_bin, is_free, render
from lesson01_moving import DIRECTIONS, move, manhattan


def neighbors(room, pos, blocked=()):
    """Free squares one step N/S/E/W from pos, skipping anything in `blocked`.
    Check the directions in the order N, S, E, W."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 6: write this function")


def bfs_path(room, start, goal, blocked=()):
    """Breadth-first search: explore squares in rings of distance 1, 2, 3 ...
    Use a queue (deque), and a dict `came_from` mapping each square to the square we reached it from.
    Return the list of squares from start to goal (both included), or None if unreachable."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 6: write this function")


def astar_path(room, start, goal, blocked=()):
    """A*: like BFS, but always expand the square with the smallest
    (steps so far + manhattan distance to goal). Use heapq as a priority queue.
    Return (path, expanded), where expanded = how many squares you took off the queue."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 6: write this function")


def path_to_commands(path):
    """Turn a path of squares into a command string like "EESW"."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 6: write this function")


if __name__ == "__main__":
    goal = find_bin(ROOM)
    path = bfs_path(ROOM, ROBOT_START, goal)
    print(render(ROOM, ROBOT_START, OBJECTS, path))
    print("BFS steps:", len(path) - 1, "| commands:", path_to_commands(path))
    apath, expanded = astar_path(ROOM, ROBOT_START, goal)
    print("A* steps:", len(apath) - 1, "| squares expanded:", expanded)
