"""Lesson 13: teaching an old model a new trick. Fine-tuning, and LoRA.

The factory trained a model W (a 6x6 table of numbers) that turns the robot's 6 sensor readings
into 6 "danger levels" (one per direction). It works on the factory robots.
Your robot is slightly different: one sensor is mounted at an angle, so its readings leak into
the others. The old model now gets things wrong.

Two ways to fix it:
  FULL FINE-TUNING: re-train all 36 numbers in W.
  LoRA: keep W frozen and add a tiny correction  A @ B,  where A is 6x1 and B is 1x6 (12 numbers).
        new output = W x + A (B x)

Big models have tables of 4096 x 4096 (16.7 million numbers each). LoRA with rank 8 trains
4096x8 + 8x4096 = 65,536 numbers instead: about 0.4%. That's why everyone uses it.
"""

import random

D = 6  # sensors in, danger levels out


# ---------- tiny matrix helpers (lists of lists) ----------

def matvec(M, x):
    """Matrix times vector: each output is the dot product of one row of M with x."""
    # BEGIN SOLUTION
    return [sum(m * xi for m, xi in zip(row, x)) for row in M]
    # END SOLUTION


def matmul(A, B):
    """Matrix times matrix: result[i][j] = sum over k of A[i][k] * B[k][j]."""
    # BEGIN SOLUTION
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
    # END SOLUTION


def add(M, N):
    """Add two matrices of the same shape, number by number."""
    # BEGIN SOLUTION
    return [[a + b for a, b in zip(r1, r2)] for r1, r2 in zip(M, N)]
    # END SOLUTION


def count_params(*matrices):
    """Total number of numbers in all the matrices."""
    # BEGIN SOLUTION
    return sum(len(M) * len(M[0]) for M in matrices)
    # END SOLUTION


# ---------- the world: a factory model, and our slightly different robot ----------

def factory_model(rng):
    """The pretrained W: mostly 'each sensor drives its own danger level', plus small cross-talk."""
    return [[(1.0 if i == j else 0.0) + rng.uniform(-0.1, 0.1) for j in range(D)] for i in range(D)]


def our_robot_truth(W):
    """What OUR robot really needs: W plus a rank-1 change (sensor 2 leaks into everything)."""
    u = [0.5, -0.3, 0.8, 0.0, -0.4, 0.2]
    v = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    return add(W, [[ui * vj for vj in v] for ui in u])


def our_robot_two_leaks(W):
    """A harder robot: TWO sensors leak (a rank-2 change). Can a rank-1 LoRA fix it?"""
    u2 = [0.0, 0.6, 0.0, -0.5, 0.3, 0.0]
    v2 = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    return add(our_robot_truth(W), [[ui * vj for vj in v2] for ui in u2])


def make_examples(W_true, n, rng):
    """n (sensor_readings, correct_danger_levels) pairs measured on our robot."""
    out = []
    for _ in range(n):
        x = [rng.uniform(0, 1) for _ in range(D)]
        out.append((x, matvec(W_true, x)))
    return out


# ---------- the model, and training ----------

def lora_forward(W, A, B, x):
    """Output = W x + A (B x). Never build A @ B: multiplying through the thin middle is cheaper."""
    # BEGIN SOLUTION
    bx = matvec(B, x)
    return [w + a for w, a in zip(matvec(W, x), matvec(A, bx))]
    # END SOLUTION


def mse(predict, examples):
    """Mean squared error over every output number of every example. predict is a function x -> outputs."""
    # BEGIN SOLUTION
    total, count = 0.0, 0
    for x, y in examples:
        for p, t in zip(predict(x), y):
            total += (p - t) ** 2
            count += 1
    return total / count
    # END SOLUTION


def train_lora(W, examples, rank=1, lr=0.05, steps=400, rng=None):
    """Keep W frozen. A starts small and random (D x rank), B starts at ZERO (rank x D),
    so at step 0 the model is exactly the factory model.
    Each step, for each example (x, y):
        bx  = B x                      (rank numbers)
        err = lora_forward(...) - y    (D numbers)
        A[i][r] -= lr * err[i] * bx[r]
        B[r][j] -= lr * (sum over i of A[i][r] * err[i]) * x[j]     (use A from BEFORE this update)
    Return (A, B)."""
    # BEGIN SOLUTION
    rng = rng or random.Random(0)
    A = [[rng.uniform(-0.1, 0.1) for _ in range(rank)] for _ in range(D)]
    B = [[0.0] * D for _ in range(rank)]
    for _ in range(steps):
        for x, y in examples:
            bx = matvec(B, x)
            err = [p - t for p, t in zip(lora_forward(W, A, B, x), y)]
            back = [sum(A[i][r] * err[i] for i in range(D)) for r in range(rank)]
            for i in range(D):
                for r in range(rank):
                    A[i][r] -= lr * err[i] * bx[r]
            for r in range(rank):
                for j in range(D):
                    B[r][j] -= lr * back[r] * x[j]
    return A, B
    # END SOLUTION


def train_full(W, examples, lr=0.05, steps=400):
    """For comparison: copy W and train ALL of it.
    Each step, for each example: err = W x - y, then W[i][j] -= lr * err[i] * x[j]."""
    W2 = [row[:] for row in W]
    for _ in range(steps):
        for x, y in examples:
            err = [p - t for p, t in zip(matvec(W2, x), y)]
            for i in range(D):
                for j in range(D):
                    W2[i][j] -= lr * err[i] * x[j]
    return W2


if __name__ == "__main__":
    rng = random.Random(0)
    W = factory_model(rng)
    truth = our_robot_truth(W)
    train, test = make_examples(truth, 12, rng), make_examples(truth, 200, rng)
    print(f"factory model on OUR robot:   test error {mse(lambda x: matvec(W, x), test):.4f}")
    A, B = train_lora(W, train, rank=1)
    print(f"LoRA rank 1 ({count_params(A, B)} numbers trained): test error {mse(lambda x: lora_forward(W, A, B, x), test):.4f}")
    W2 = train_full(W, train)
    print(f"full fine-tune ({count_params(W2)} numbers trained): test error {mse(lambda x: matvec(W2, x), test):.4f}")
    harder = our_robot_two_leaks(W)
    train2, test2 = make_examples(harder, 12, rng), make_examples(harder, 200, rng)
    for rank in (1, 2):
        A2, B2 = train_lora(W, train2, rank=rank)
        print(f"two leaky sensors, LoRA rank {rank}: test error {mse(lambda x: lora_forward(W, A2, B2, x), test2):.4f}")
    for d, r in [(6, 1), (4096, 8)]:
        print(f"a {d}x{d} layer: full = {d * d:,} numbers, LoRA rank {r} = {2 * d * r:,} ({2 * d * r / (d * d):.1%})")
