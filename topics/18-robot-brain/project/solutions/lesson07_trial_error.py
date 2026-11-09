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
    # BEGIN SOLUTION
    return max(ACTIONS, key=lambda a: (Q.get((pos, a), 0.0), -ACTIONS.index(a)))
    # END SOLUTION


def choose_action(Q, pos, epsilon, rng):
    """Explore or exploit: with probability epsilon pick rng.choice(ACTIONS),
    otherwise pick best_action."""
    # BEGIN SOLUTION
    if rng.random() < epsilon:
        return rng.choice(ACTIONS)
    return best_action(Q, pos)
    # END SOLUTION


def q_update(Q, pos, action, reward, next_pos, alpha, gamma, done):
    """The Q-learning rule:
        target = reward                                   if done
        target = reward + gamma * max_a Q[(next_pos, a)]   otherwise
        Q[(pos, action)] += alpha * (target - Q[(pos, action)])
    (Missing Q values count as 0.)"""
    # BEGIN SOLUTION
    old = Q.get((pos, action), 0.0)
    target = reward if done else reward + gamma * max(Q.get((next_pos, a), 0.0) for a in ACTIONS)
    Q[(pos, action)] = old + alpha * (target - old)
    # END SOLUTION


def q_learn(room, start, goal, episodes=300, alpha=0.5, gamma=0.95, epsilon=0.2, rng=None, max_steps=200):
    """Run many episodes. Each episode: start at `start`, repeatedly choose_action,
    move with safe_move, reward = 10 if you reached goal else -1, q_update,
    stop when you reach goal or after max_steps. Return (Q, steps_per_episode)."""
    # BEGIN SOLUTION
    rng = rng or random.Random(0)
    Q, steps_log = {}, []
    for _ in range(episodes):
        pos, steps = start, 0
        while steps < max_steps:
            a = choose_action(Q, pos, epsilon, rng)
            nxt = safe_move(room, pos, a)
            done = nxt == goal
            q_update(Q, pos, a, 10.0 if done else -1.0, nxt, alpha, gamma, done)
            pos, steps = nxt, steps + 1
            if done:
                break
        steps_log.append(steps)
    return Q, steps_log
    # END SOLUTION


def greedy_path(Q, room, start, goal, max_steps=100):
    """Follow best_action from start until goal (or max_steps). Return the list of squares."""
    # BEGIN SOLUTION
    path, pos = [start], start
    while pos != goal and len(path) <= max_steps:
        pos = safe_move(room, pos, best_action(Q, pos))
        path.append(pos)
    return path
    # END SOLUTION


if __name__ == "__main__":
    start, goal = find_char(MAZE, "S"), find_char(MAZE, "G")
    Q, log = q_learn(MAZE, start, goal, rng=random.Random(0))
    print("steps in first 5 episodes:", log[:5], "| last 5:", log[-5:])
    path = greedy_path(Q, MAZE, start, goal)
    print(render(MAZE, None, None, path))
    print("learned route length:", len(path) - 1)
