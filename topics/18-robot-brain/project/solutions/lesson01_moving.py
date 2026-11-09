"""Lesson 1: where is the robot? Coordinates and moving on a grid."""

from world import ROOM, ROBOT_START, OBJECTS, is_free, render

# Each direction is a change in (x, y). Remember: y grows DOWNWARDS.
DIRECTIONS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}


def move(pos, direction):
    """Return the new (x, y) after one step in direction 'N', 'S', 'E' or 'W'.
    Doesn't check walls: just the maths.

    move((2, 3), "E") -> (3, 3)
    move((2, 3), "N") -> (2, 2)
    """
    # BEGIN SOLUTION
    dx, dy = DIRECTIONS[direction]
    return (pos[0] + dx, pos[1] + dy)
    # END SOLUTION


def safe_move(room, pos, direction):
    """Like move(), but if the new square is a wall (or outside the room),
    the robot stays where it is. Use is_free(room, new_pos)."""
    # BEGIN SOLUTION
    new_pos = move(pos, direction)
    return new_pos if is_free(room, new_pos) else pos
    # END SOLUTION


def follow(room, start, commands):
    """Follow a string of commands like "EESSW" using safe_move.
    Return the list of every position visited, including the start.

    follow(ROOM, (1, 1), "EE") -> [(1, 1), (2, 1), (3, 1)]
    """
    # BEGIN SOLUTION
    path = [start]
    pos = start
    for c in commands:
        pos = safe_move(room, pos, c)
        path.append(pos)
    return path
    # END SOLUTION


def manhattan(a, b):
    """Grid distance between a and b when you can only move N/S/E/W
    (ignoring walls): |x1 - x2| + |y1 - y2|."""
    # BEGIN SOLUTION
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # END SOLUTION


if __name__ == "__main__":
    path = follow(ROOM, ROBOT_START, "EEEESSS")
    print(render(ROOM, path[-1], OBJECTS, path))
    print("Ended at", path[-1], "| distance to red block:", manhattan(path[-1], OBJECTS["red block"]))
