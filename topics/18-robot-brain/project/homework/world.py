"""The Robo-Helper world. Provided for you: you don't need to change this file.

The room is a grid of characters:
    #  wall
    .  free floor
    B  the bin (where things get put away)
Objects (blocks) sit on free squares and are stored separately, so they can move.

Coordinates are (x, y): x grows to the right, y grows downwards. (0, 0) is the top-left corner.
"""

ROOM = [
    "##########",
    "#........#",
    "#..##....#",
    "#..#.....#",
    "#....##..#",
    "#........#",
    "#.#....B.#",
    "##########",
]

# name -> (x, y)
OBJECTS = {
    "red block": (2, 1),
    "blue block": (6, 3),
    "green block": (1, 5),
}

ROBOT_START = (1, 1)


def find_bin(room):
    """Return the (x, y) of the bin 'B'."""
    for y, row in enumerate(room):
        x = row.find("B")
        if x != -1:
            return (x, y)
    return None


def is_free(room, pos):
    """True if pos is inside the room and not a wall."""
    x, y = pos
    if y < 0 or y >= len(room) or x < 0 or x >= len(room[0]):
        return False
    return room[y][x] != "#"


def render(room, robot=None, objects=None, path=None):
    """Draw the room as text. R = robot, letters = objects, * = path."""
    grid = [list(row) for row in room]
    for (x, y) in path or []:
        if grid[y][x] == ".":
            grid[y][x] = "*"
    for name, (x, y) in (objects or {}).items():
        grid[y][x] = name[0].lower()
    if robot:
        x, y = robot
        grid[y][x] = "R"
    return "\n".join("".join(row) for row in grid)


if __name__ == "__main__":
    print(render(ROOM, ROBOT_START, OBJECTS))
