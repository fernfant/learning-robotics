"""Lesson 0: your first robot algorithm.

An algorithm is just a list of exact steps. Computers follow them perfectly,
so the steps have to be right.
"""


def introduce(name):
    """Return the robot's greeting, e.g. introduce("Robo") -> "Hello, I am Robo!"."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 0: write this function")


def steps_to_wall(start_x, wall_x):
    """The robot stands at start_x and walks right one square at a time.
    It must stop on the square just BEFORE the wall at wall_x.
    Return how many steps it takes. Use a loop, not subtraction!

    steps_to_wall(1, 5) -> 3   (1 -> 2 -> 3 -> 4, then the wall is next)
    """
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 0: write this function")


if __name__ == "__main__":
    print(introduce("Robo"))
    print("Steps to wall:", steps_to_wall(1, 5))
