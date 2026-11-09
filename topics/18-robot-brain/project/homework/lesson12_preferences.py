"""Lesson 12: learning what people prefer. Reinforcement learning from human feedback, by hand.

There are many routes to the bin. Which one is "best"? Shortest isn't the whole story:
people might prefer routes that keep away from walls (fewer scrapes) and have fewer turns (smoother).
Nobody can write the perfect rule down, but anyone can say "I like route A more than route B".

The recipe (the same idea used to train ChatGPT-style assistants):
  1. show a person two options, record which they prefer
  2. learn a REWARD MODEL that scores options so that preferred ones score higher
  3. let the robot pick the option with the highest learned reward
"""

import math
import random

from world import ROOM, ROBOT_START, find_bin, is_free
from lesson01_moving import move
from lesson04_neuron import sigmoid
from lesson06_paths import astar_path

# The "person" we simulate. In real life you'd ask a human! Negative = they dislike it.
# Per route: -1.0 per step, -0.6 per step that brushes a wall, -0.8 per turn.
TRUE_TASTE = (-1.0, -0.6, -0.8)


def route_features(room, path):
    """Describe a route with 3 numbers: (length, near_wall, turns)
      length    = number of steps (len(path) - 1)
      near_wall = number of squares on the path (after the start) with a wall directly N, S, E or W
      turns     = number of times the direction of travel changes"""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 12: write this function")


def candidate_routes(room, start, goal):
    """Different routes: A* from start to goal through each free waypoint (x, y) in the room.
    Join the two halves (don't repeat the waypoint) and drop duplicates. Some routes wander into a
    corner and come back: that's fine, they're real (bad) options a person might be shown. Return a list of paths."""
    routes, seen = [], set()
    for y in range(len(room)):
        for x in range(len(room[0])):
            wp = (x, y)
            if not is_free(room, wp):
                continue
            a, _ = astar_path(room, start, wp)
            b, _ = astar_path(room, wp, goal)
            if a is None or b is None:
                continue
            path = a + b[1:]
            key = tuple(path)
            if key not in seen:
                seen.add(key)
                routes.append(path)
    return routes


def reward(weights, features):
    """The reward model: a weighted sum, w1*f1 + w2*f2 + w3*f3."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 12: write this function")


def prob_prefers_a(weights, feats_a, feats_b):
    """Chance a person picks A over B: sigmoid(reward(A) - reward(B)).
    (This is the Bradley-Terry model: bigger reward gap = more certain choice.)"""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 12: write this function")


def ask_person(feats_a, feats_b, rng):
    """Simulate a person with TRUE_TASTE: return 1 if they choose A, else 0.
    People are a bit random, so choose A with probability prob_prefers_a(TRUE_TASTE, A, B)."""
    return 1 if rng.random() < prob_prefers_a(TRUE_TASTE, feats_a, feats_b) else 0


def train_reward_model(comparisons, lr=0.01, epochs=300):
    """Learn weights from comparisons, a list of (feats_a, feats_b, chose_a).
    Start with weights [0, 0, 0]. For each epoch, for each comparison:
        p = prob_prefers_a(weights, feats_a, feats_b)
        for each i: weights[i] += lr * (chose_a - p) * (feats_a[i] - feats_b[i])
    (Exactly like Lesson 4's neuron, but on the DIFFERENCE between A and B.) Return weights."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 12: write this function")


def agreement(weights, comparisons):
    """Fraction of comparisons where the model's favourite (reward(A) > reward(B)) matches the person's choice."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 12: write this function")


def best_route(weights, room, routes):
    """The route with the highest learned reward."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 12: write this function")


def collect_comparisons(room, routes, n, rng):
    """Show the 'person' n random pairs of routes and record their choices."""
    feats = [route_features(room, r) for r in routes]
    out = []
    for _ in range(n):
        i, j = rng.sample(range(len(routes)), 2)
        out.append((feats[i], feats[j], ask_person(feats[i], feats[j], rng)))
    return out


if __name__ == "__main__":
    rng = random.Random(0)
    routes = candidate_routes(ROOM, ROBOT_START, find_bin(ROOM))
    print(len(routes), "different routes to the bin")
    train, test = collect_comparisons(ROOM, routes, 150, rng), collect_comparisons(ROOM, routes, 100, rng)
    w = train_reward_model(train)
    print("learned taste:", [round(v, 2) for v in w], "| true taste:", TRUE_TASTE)
    print(f"agrees with the person on NEW comparisons: {agreement(w, test):.0%}")
    shortest, _ = astar_path(ROOM, ROBOT_START, find_bin(ROOM))
    pick = best_route(w, ROOM, routes)
    print("shortest route features (length, near_wall, turns):", route_features(ROOM, shortest))
    print("robot's chosen route features:                     ", route_features(ROOM, pick))
