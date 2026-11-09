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
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 1: write this function")


def safe_move(room, pos, direction):
    """Like move(), but if the new square is a wall (or outside the room),
    the robot stays where it is. Use is_free(room, new_pos)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 1: write this function")


def follow(room, start, commands):
    """Follow a string of commands like "EESSW" using safe_move.
    Return the list of every position visited, including the start.

    follow(ROOM, (1, 1), "EE") -> [(1, 1), (2, 1), (3, 1)]
    """
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 1: write this function")


def manhattan(a, b):
    """Grid distance between a and b when you can only move N/S/E/W
    (ignoring walls): |x1 - x2| + |y1 - y2|."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 1: write this function")


if __name__ == "__main__":
    path = follow(ROOM, ROBOT_START, "EEEESSS")
    print(render(ROOM, path[-1], OBJECTS, path))
    print("Ended at", path[-1], "| distance to red block:", manhattan(path[-1], OBJECTS["red block"]))
