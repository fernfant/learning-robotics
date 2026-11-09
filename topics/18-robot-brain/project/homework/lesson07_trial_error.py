"""Lesson 7: learning by trial and error. Q-learning in a maze.

No map, no planner: the robot only gets rewards. -1 per step, +10 at the goal.
It learns Q[(square, action)] = "how good is doing this action here?".
"""

import random

from world import is_free, render
from lesson01_moving import safe_move

ACTIONS = "NSEW"

MAZE = [
    "#######",
    "#S..#.#",
    "#.#.#.#",
    "#.#...#",
    "#...#G#",
    "#######",
]


def find_char(room, ch):
    for y, row in enumerate(room):
        if ch in row:
            return (row.index(ch), y)
    return None


def best_action(Q, pos):
    """The action with the highest Q value at pos (Q values default to 0).
    On a tie, pick the first in ACTIONS order."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 7: write this function")


def choose_action(Q, pos, epsilon, rng):
    """Explore or exploit: with probability epsilon pick rng.choice(ACTIONS),
    otherwise pick best_action."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 7: write this function")


def q_update(Q, pos, action, reward, next_pos, alpha, gamma, done):
    """The Q-learning rule:
        target = reward                                   if done
        target = reward + gamma * max_a Q[(next_pos, a)]   otherwise
        Q[(pos, action)] += alpha * (target - Q[(pos, action)])
    (Missing Q values count as 0.)"""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 7: write this function")


def q_learn(room, start, goal, episodes=300, alpha=0.5, gamma=0.95, epsilon=0.2, rng=None, max_steps=200):
    """Run many episodes. Each episode: start at `start`, repeatedly choose_action,
    move with safe_move, reward = 10 if you reached goal else -1, q_update,
    stop when you reach goal or after max_steps. Return (Q, steps_per_episode)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 7: write this function")


def greedy_path(Q, room, start, goal, max_steps=100):
    """Follow best_action from start until goal (or max_steps). Return the list of squares."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 7: write this function")


if __name__ == "__main__":
    start, goal = find_char(MAZE, "S"), find_char(MAZE, "G")
    Q, log = q_learn(MAZE, start, goal, rng=random.Random(0))
    print("steps in first 5 episodes:", log[:5], "| last 5:", log[-5:])
    path = greedy_path(Q, MAZE, start, goal)
    print(render(MAZE, None, None, path))
    print("learned route length:", len(path) - 1)
