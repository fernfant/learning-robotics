"""Check your homework.

    python3 check.py 3        check lesson 3
    python3 check.py all      check every lesson
    python3 check.py 15a      check a stretch (15a attention, 19a AI judge)
    python3 check.py robot    check YOUR robot (my_robot.py): one check per week's piece
    python3 check.py 3 --solutions   check the reference solutions instead (for teachers)

Run it from the project folder (the one that contains this file).
"""

import importlib
import math
import random
import re
import sys
from pathlib import Path

GREEN, RED, YELLOW, END = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


class Fail(Exception):
    pass


def expect(cond, hint):
    if not cond:
        raise Fail(hint)


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ---------- one function per lesson: a list of (name, test) ----------

def lesson00(m):
    return [
        ("introduce", lambda: expect(m.introduce("Robo") == "Hello, I am Robo!",
                                     'introduce("Robo") should return exactly "Hello, I am Robo!"')),
        ("steps_to_wall", lambda: [expect(m.steps_to_wall(1, 5) == 3, "steps_to_wall(1, 5) should be 3"),
                                   expect(m.steps_to_wall(4, 5) == 0, "already next to the wall: steps_to_wall(4, 5) should be 0"),
                                   expect(m.steps_to_wall(0, 10) == 9, "steps_to_wall(0, 10) should be 9")]),
    ]


def lesson01(m):
    from world import ROOM
    return [
        ("move", lambda: [expect(m.move((2, 3), "E") == (3, 3), 'move((2, 3), "E") should be (3, 3)'),
                          expect(m.move((2, 3), "N") == (2, 2), 'move((2, 3), "N") should be (2, 2): remember y grows DOWN'),
                          expect(m.move((2, 3), "W") == (1, 3), 'move((2, 3), "W") should be (1, 3)')]),
        ("safe_move", lambda: [expect(m.safe_move(ROOM, (1, 1), "N") == (1, 1), "moving into the top wall should leave the robot at (1, 1)"),
                               expect(m.safe_move(ROOM, (1, 1), "E") == (2, 1), "moving E from (1, 1) should reach (2, 1)")]),
        ("follow", lambda: [expect(m.follow(ROOM, (1, 1), "EE") == [(1, 1), (2, 1), (3, 1)], 'follow(ROOM, (1, 1), "EE") should list 3 positions'),
                            expect(m.follow(ROOM, (1, 1), "NW")[-1] == (1, 1), "bumping into walls should keep the robot in place"),
                            expect(m.follow(ROOM, (1, 1), "") == [(1, 1)], "no commands: the path is just the start")]),
        ("manhattan", lambda: [expect(m.manhattan((1, 1), (4, 5)) == 7, "manhattan((1, 1), (4, 5)) should be 3 + 4 = 7"),
                               expect(m.manhattan((4, 5), (1, 1)) == 7, "distance shouldn't depend on order: use abs()")]),
    ]


def lesson02(m):
    from world import ROOM
    return [
        ("distance_to_wall", lambda: [expect(m.distance_to_wall(ROOM, (1, 1), "E") == 7, "from (1, 1) facing E there are 7 free squares"),
                                      expect(m.distance_to_wall(ROOM, (1, 1), "N") == 0, "facing a wall directly: 0"),
                                      expect(m.distance_to_wall(ROOM, (1, 1), "S") == 5, "from (1, 1) facing S there are 5 free squares")]),
        ("noisy_reading", lambda: [expect(all(4 <= m.noisy_reading(5, 1.0, random.Random(i)) <= 6 for i in range(50)), "readings must stay within true ± noise"),
                                   expect(all(m.noisy_reading(0.2, 1.0, random.Random(i)) >= 0 for i in range(50)), "never return a negative distance")]),
        ("average", lambda: [expect(close(m.average([1, 2, 3, 4]), 2.5), "average([1, 2, 3, 4]) should be 2.5")]),
        ("averaging helps", lambda: expect(
            m.average_error(5, 1.0, 16, 300, random.Random(0)) < m.average_error(5, 1.0, 1, 300, random.Random(0)) / 2,
            "averaging 16 readings should cut the typical error by more than half")),
    ]


def lesson03(m):
    return [
        ("predict", lambda: expect(close(m.predict(2, 1, 3), 7), "predict(2, 1, 3) = 2*3 + 1 = 7")),
        ("mse", lambda: [expect(close(m.mse(1, 0, [(1, 1), (2, 2)]), 0), "a perfect line has mse 0"),
                         expect(close(m.mse(0, 0, [(1, 1), (2, 3)]), 5), "mse(0, 0, [(1,1),(2,3)]) = (1 + 9) / 2 = 5")]),
        ("gradients", lambda: [expect(all(close(g, e) for g, e in zip(m.gradients(0, 0, [(1, 1), (2, 3)]), (-7, -4))),
                                      "gradients(0, 0, [(1,1),(2,3)]) should be (-7.0, -4.0)")]),
        ("fit_line learns", lambda: [
            expect(abs(m.fit_line(m.STOP_DATA)[0] - 0.81) < 0.05, "the learned w should be about 0.81"),
            expect(m.fit_line(m.STOP_DATA)[2][-1] < m.fit_line(m.STOP_DATA)[2][0], "the error should go DOWN during training")]),
        ("max_safe_speed", lambda: [expect(m.max_safe_speed(1, 0, 1.0) == 0.8, "with w=1, b=0, 1.0 m free and 0.2 margin -> 0.8"),
                                    expect(m.max_safe_speed(1, 0, 0.1) == 0.0, "no room at all -> speed 0")]),
    ]


def lesson04(m):
    def trained():
        data = m.make_obstacle_data(450, random.Random(2))
        return m.train_neuron(data)
    return [
        ("sigmoid", lambda: [expect(close(m.sigmoid(0), 0.5), "sigmoid(0) should be 0.5"),
                             expect(m.sigmoid(10) > 0.99 and m.sigmoid(-10) < 0.01, "sigmoid should approach 1 and 0"),
                             expect(m.sigmoid(-1000) >= 0, "sigmoid(-1000) crashed or went negative: handle big negative z")]),
        ("neuron", lambda: expect(close(m.neuron([1, 1], 0, (0, 0)), 0.5) and m.neuron([1, -1], 0, (5, 0)) > 0.99,
                                  "neuron = sigmoid(w1*x1 + w2*x2 + bias)")),
        ("train_neuron", lambda: (lambda wb: [
            expect(m.neuron(*wb, (0.5, 0.0)) > 0.8, "after training, an obstacle 0.5 m away should give stop-probability > 0.8"),
            expect(m.neuron(*wb, (6.0, 0.2)) < 0.1, "something 6 m away and slow should give a low stop-probability")])(trained())),
        ("should_stop", lambda: expect(m.should_stop([0, 0], 0, (1, 1), 0.5) and not m.should_stop([0, 0], 0, (1, 1), 0.6),
                                       "should_stop compares the probability with the threshold (>=)")),
    ]


def lesson05(m):
    import lesson04_neuron as n4
    return [
        ("train_test_split", lambda: (lambda d: (lambda tt: [
            expect(len(tt[1]) == 25 and len(tt[0]) == 75, "test_fraction 0.25 of 100 -> 25 test, 75 train"),
            expect(sorted(tt[0] + tt[1]) == sorted(d), "train + test must contain every example exactly once"),
            expect(d == list(range(100)), "don't shuffle the original list: shuffle a copy")])(m.train_test_split(d, 0.25, random.Random(0))))(list(range(100)))),
        ("confusion", lambda: expect(m.confusion([1, 1, 0, 0, 1], [1, 0, 1, 0, 1]) == (2, 1, 1, 1), "expected (tp, fp, fn, tn) = (2, 1, 1, 1)")),
        ("metrics", lambda: [expect(close(m.accuracy(2, 1, 1, 1), 0.6), "accuracy = (tp + tn) / all"),
                             expect(close(m.precision(2, 1, 1, 1), 2 / 3), "precision = tp / (tp + fp)"),
                             expect(close(m.recall(2, 1, 1, 1), 2 / 3), "recall = tp / (tp + fn)"),
                             expect(m.precision(0, 0, 3, 5) == 0.0, "precision with no 'stop' predictions should be 0, not a crash")]),
        ("safest_threshold", lambda: (lambda data: (lambda wb: (lambda t: [
            expect(t < 0.5, f"for safety the threshold should drop below 0.5 (got {t})"),
            expect(m.evaluate(*wb, data, t)["recall"] >= 0.97, "at the chosen threshold, recall should be at least 0.97")])(
            m.safest_threshold(*wb, data)))(n4.train_neuron(data)))(n4.make_obstacle_data(450, random.Random(2)))),
    ]


def lesson06(m):
    from world import ROOM, ROBOT_START, find_bin
    goal = find_bin(ROOM)
    return [
        ("neighbors", lambda: [expect(m.neighbors(ROOM, (1, 1)) == [(1, 2), (2, 1)], "neighbors of (1, 1) are (1, 2) then (2, 1), checking N, S, E, W"),
                               expect(m.neighbors(ROOM, (1, 1), blocked={(2, 1)}) == [(1, 2)], "skip blocked squares")]),
        ("bfs_path", lambda: (lambda p: [expect(p is not None and p[0] == ROBOT_START and p[-1] == goal, "the path must start at the start and end at the goal"),
                                         expect(len(p) - 1 == 11, f"the shortest route to the bin is 11 steps (got {len(p) - 1 if p else None})"),
                                         expect(all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(p, p[1:])), "each step must move exactly one square")])(m.bfs_path(ROOM, ROBOT_START, goal))),
        ("bfs unreachable", lambda: expect(m.bfs_path(ROOM, (1, 1), (8, 6), blocked={(1, 2), (2, 1)}) is None, "a boxed-in robot should get None")),
        ("astar_path", lambda: (lambda r: [expect(r[0] is not None and len(r[0]) - 1 == 11, "A* should also find the 11-step route"),
                                           expect(isinstance(r[1], int) and r[1] > 0, "return (path, expanded)")])(m.astar_path(ROOM, ROBOT_START, goal))),
        ("path_to_commands", lambda: expect(m.path_to_commands([(1, 1), (2, 1), (2, 2), (1, 2)]) == "ESW", "[(1,1),(2,1),(2,2),(1,2)] -> 'ESW'")),
    ]


def lesson07(m):
    return [
        ("best_action", lambda: [expect(m.best_action({}, (1, 1)) == "N", "all zeros: pick the first action, 'N'"),
                                 expect(m.best_action({((1, 1), "E"): 2.0}, (1, 1)) == "E", "pick the action with the highest Q")]),
        ("choose_action", lambda: expect(m.choose_action({((1, 1), "W"): 5.0}, (1, 1), 0.0, random.Random(0)) == "W", "epsilon 0 means always exploit")),
        ("q_update", lambda: (lambda Q: [m.q_update(Q, (1, 1), "E", -1.0, (2, 1), 0.5, 0.9, False),
                                         expect(close(Q[((1, 1), "E")], -0.5 + 0.5 * 0.9 * 4.0), "target = -1 + 0.9 * 4; Q moves halfway there"),
                                         ])({((2, 1), "S"): 4.0})),
        ("q_learn finds the shortcut", lambda: (lambda s, g: (lambda Ql: [
            expect(len(m.greedy_path(Ql[0], m.MAZE, s, g)) - 1 == 7, "after training, the greedy route should be the shortest: 7 steps"),
            expect(sum(Ql[1][-20:]) / 20 < sum(Ql[1][:20]) / 20, "episodes should get shorter as the robot learns")])(
            m.q_learn(m.MAZE, s, g, rng=random.Random(0))))(m.find_char(m.MAZE, "S"), m.find_char(m.MAZE, "G"))),
    ]


def lesson08(m):
    return [
        ("tokenize", lambda: expect(m.tokenize("The cat. Sat") == ["the", "cat", ".", "sat"], 'tokenize("The cat. Sat") -> ["the", "cat", ".", "sat"]')),
        ("count_bigrams", lambda: expect(m.count_bigrams(["a", "b", "a", "b", "c"]) == {"a": {"b": 2}, "b": {"a": 1, "c": 1}},
                                         "count_bigrams(['a','b','a','b','c']) should be {'a': {'b': 2}, 'b': {'a': 1, 'c': 1}}")),
        ("next_word_probs", lambda: [expect(m.next_word_probs({"b": {"a": 1, "c": 3}}, "b") == {"a": 0.25, "c": 0.75}, "1 and 3 -> 0.25 and 0.75"),
                                     expect(m.next_word_probs({}, "zzz") == {}, "unknown word -> {}")]),
        ("generate", lambda: (lambda c: [expect(m.generate(c, "the", 5, random.Random(0)).split()[0] == "the", "start with the start word"),
                                         expect(len(m.generate(c, "the", 5, random.Random(0)).split()) == 6, "start word + 5 new words"),
                                         expect(m.generate(c, "zzz", 5, random.Random(0)) == "zzz", "stop when there are no options")])(m.count_bigrams(m.tokenize(m.STORY)))),
        ("edits1", lambda: (lambda e: [expect("cat" in e and "at" in e and "act" in e and "cart" in e, "'cat' itself, a delete ('at'), a swap ('act') and an insert ('cart') must all be there"),
                                       expect("bat" in e, "replacing one letter: 'cat' -> 'bat'"),
                                       expect(all(abs(len(w) - 3) <= 1 for w in e), "one typo changes the length by at most 1"),
                                       expect(len(m.edits1("ab")) == 130, f"'ab' has exactly 130 different one-typo versions, got {len(m.edits1('ab'))}")])(m.edits1("cat"))),
        ("fix_typos", lambda: (lambda c: [expect(m.fix_typos("put teh red blok", c) == "put the red block", "'put teh red blok' -> 'put the red block'"),
                                          expect(m.fix_typos("put the purple block", c) == "put the purple block", "known words and hopeless words stay as they are"),
                                          expect(m.fix_word("bok", "red", {"red": {"box": 1, "block": 3}}, {"red", "box", "block"}) == "box",
                                                 "'bok' is one typo from 'box' but two from 'block' -> 'box'")])(
            m.count_bigrams(m.tokenize("put the red block in the bin . put the blue block in the bin")))),
    ]


def lesson09(m):
    return [
        ("train_intent_model", lambda: (lambda md: [expect(md["intent_counts"]["stop"] == 8, "there are 8 'stop' examples in TRAIN"),
                                                     expect(md["word_counts"]["put"]["bin"] >= 4, "'bin' appears in several 'put' examples"),
                                                     expect("halt" in md["vocab"], "vocab should contain every word seen")])(m.train_intent_model(m.TRAIN))),
        ("predict_intent", lambda: (lambda md: [expect(m.predict_intent(md, "put the red block in the bin") == "put", "clear 'put' command"),
                                                 expect(m.predict_intent(md, "stop") == "stop", "clear 'stop' command")])(m.train_intent_model(m.TRAIN))),
        ("extract_object", lambda: [expect(m.extract_object("grab the Blue one") == "blue block", "'grab the Blue one' -> 'blue block'"),
                                    expect(m.extract_object("stop") is None, "no colour -> None")]),
        ("parse_command", lambda: expect(m.parse_command(m.train_intent_model(m.TRAIN), "stop now") == {"intent": "stop", "object": None}, "stop has no object")),
        ("test accuracy", lambda: (lambda acc: expect(acc >= 0.8, f"test accuracy should be at least 0.8 (got {acc:.2f})"))(
            m.test_accuracy(m.train_intent_model(m.TRAIN), m.TEST))),
    ]


def lesson10(m):
    known = {"red block", "blue block", "green block"}
    return [
        ("extract_json", lambda: [expect(m.extract_json('Sure! {"intent": "stop", "object": null} ok') == {"intent": "stop", "object": None}, "find the JSON inside chatty text"),
                                  expect(m.extract_json("no json here") is None, "no JSON -> None"),
                                  expect(m.extract_json('{"intent": "put" "object": 1}') is None, "broken JSON -> None, not a crash")]),
        ("validate_action", lambda: [expect(m.validate_action({"intent": "put", "object": "red block"}, known)[0], "a valid action"),
                                     expect(not m.validate_action({"intent": "throw", "object": "red block"}, known)[0], "unknown intent must fail"),
                                     expect(not m.validate_action({"intent": "put", "object": "purple block"}, known)[0], "unknown object must fail"),
                                     expect(not m.validate_action({"intent": "go", "object": "red block", "also": "x"}, known)[0], "extra keys must fail"),
                                     expect(not m.validate_action({"intent": "go", "object": None}, known)[0], "'go' needs an object"),
                                     expect(not m.validate_action(None, known)[0], "None must fail, not crash")]),
        ("safe_parse", lambda: [expect(m.safe_parse('{"intent": "stop", "object": null}', known)[1] == "llm", "good LLM reply -> source 'llm'"),
                                expect(m.safe_parse("garbage", known, "stop", lambda c: {"intent": "stop", "object": None})[1] == "fallback", "bad reply + good fallback -> 'fallback'"),
                                expect(m.safe_parse("garbage", known)[0] is None, "bad reply, no fallback -> None")]),
    ]


def lesson11(m):
    return [
        ("put works", lambda: (lambda r: (lambda res: [expect(res["ok"], f"'put the red block in the bin' should succeed: {res['message']}"),
                                                       expect("red block" in r.binned, "the red block should be in robot.binned")])(r.run_command("put the red block in the bin")))(m.RoboHelper())),
        ("find works", lambda: expect("(6, 3)" in m.RoboHelper().run_command("where is the blue block")["message"], "find should report (6, 3)")),
        ("refuses safely", lambda: expect(not m.RoboHelper().run_command("put the purple block away")["ok"], "an unknown object must be refused")),
        ("replans around surprises", lambda: (lambda r: [r.run_command("put the blue block in the bin"),
                                                         expect("blue block" in r.binned and r.log, "with a surprise at (4, 1) the robot should log a stop and still finish")])(m.RoboHelper(surprises={(4, 1)}))),
        ("evaluate", lambda: (lambda res: [expect(res[0] >= 0.8, f"test pass rate should be at least 80% (got {res[0]:.0%})"),
                                            expect(any("find the green block" in str(f[0]) for f in res[1]),
                                                   "'find the green block' bins the green block, which is wrong: it must be in your failures. "
                                                   "Compare with ==, not <= (robot.binned must be EXACTLY the expected set)")])(m.evaluate())),
    ]


def lesson12(m):
    import lesson06_paths as p6
    from world import ROOM, ROBOT_START, find_bin
    routes = m.candidate_routes(ROOM, ROBOT_START, find_bin(ROOM))
    return [
        ("route_features", lambda: [expect(m.route_features(ROOM, [(1, 1), (2, 1), (3, 1)]) == (2, 2, 0), "a 2-step straight run along the top wall -> (2, 2, 0)"),
                                    expect(m.route_features(ROOM, [(1, 1), (2, 1), (2, 2)])[2] == 1, "east then south is 1 turn"),
                                    expect(m.route_features(ROOM, p6.bfs_path(ROOM, ROBOT_START, find_bin(ROOM)))[0] == 11, "the shortest route has length 11")]),
        ("reward", lambda: expect(close(m.reward([-1, -0.5, -2], (10, 4, 1)), -14), "reward([-1, -0.5, -2], (10, 4, 1)) = -10 - 2 - 2 = -14")),
        ("prob_prefers_a", lambda: [expect(close(m.prob_prefers_a([1, 0, 0], (3, 0, 0), (3, 0, 0)), 0.5), "equal rewards -> 0.5"),
                                    expect(m.prob_prefers_a([-1, 0, 0], (5, 0, 0), (9, 0, 0)) > 0.95, "much shorter A, with taste -1 per step -> very likely chosen")]),
        ("learns the taste", lambda: (lambda rng: (lambda tr, te: (lambda w: [
            expect(all(v < 0 for v in w), f"all three learned weights should be negative (people dislike all three things); got {[round(v, 2) for v in w]}"),
            expect(m.agreement(w, te) >= 0.78, f"should agree with the person on new comparisons at least 78% of the time (got {m.agreement(w, te):.0%})"),
            expect(m.best_route(w, ROOM, routes) == m.best_route(m.TRUE_TASTE, ROOM, routes), "the robot should pick the same route the person likes best")])(
            m.train_reward_model(tr)))(m.collect_comparisons(ROOM, routes, 150, rng), m.collect_comparisons(ROOM, routes, 100, rng)))(random.Random(0))),
    ]


def lesson13(m):
    W = [[1, 2], [3, 4]]
    return [
        ("matvec", lambda: expect(m.matvec(W, [1, 1]) == [3, 7], "[[1,2],[3,4]] times [1,1] = [3, 7]")),
        ("matmul", lambda: [expect(m.matmul(W, [[1, 0], [0, 1]]) == W, "anything times the identity is itself"),
                            expect(m.matmul([[1], [2]], [[3, 4]]) == [[3, 4], [6, 8]], "a 2x1 times a 1x2 makes a 2x2 table")]),
        ("add + count_params", lambda: [expect(m.add(W, W) == [[2, 4], [6, 8]], "add adds number by number"),
                                        expect(m.count_params(W, [[1, 2, 3]]) == 7, "4 + 3 = 7 numbers")]),
        ("lora_forward", lambda: expect(m.lora_forward(W, [[1], [0]], [[0, 1]], [1, 1]) == [4, 7], "W x = [3, 7] plus A (B x) = [1, 0] gives [4, 7]")),
        ("mse", lambda: expect(close(m.mse(lambda x: [0, 0], [([1], [1, 3])]), 5.0), "errors 1 and 3 -> (1 + 9) / 2 = 5")),
        ("LoRA fixes our robot", lambda: (lambda rng: (lambda Wf: (lambda truth: (lambda tr, te: (lambda AB: [
            expect(m.count_params(*AB) == 12, "rank-1 LoRA on a 6x6 model trains 12 numbers"),
            expect(m.mse(lambda x: m.lora_forward(Wf, AB[0], AB[1], x), te) < 0.1 * m.mse(lambda x: m.matvec(Wf, x), te),
                   "after training, LoRA's test error should be under a tenth of the factory model's")])(
            m.train_lora(Wf, tr, rank=1)))(m.make_examples(truth, 12, rng), m.make_examples(truth, 200, rng)))(m.our_robot_truth(Wf)))(m.factory_model(rng)))(random.Random(0))),
    ]


def lesson15(m):
    from lesson09_commands import TEST
    tiny = lambda: m.TinyLM({"red", "block"})
    return [
        ("softmax", lambda: [expect(all(close(a, b) for a, b in zip(m.softmax([0, 0]), [0.5, 0.5])), "softmax([0, 0]) should be [0.5, 0.5]"),
                             expect(close(sum(m.softmax([1, 2, 3])), 1.0), "probabilities must add up to 1"),
                             expect(close(m.softmax([1000, 1000])[0], 0.5), "softmax([1000, 1000]) crashed or was wrong: subtract the biggest score first")]),
        ("read", lambda: (lambda t: [expect(all(close(v, (a + b) / 2) for v, a, b in zip(t.read("red block"), t.word_emb["red"], t.word_emb["block"])),
                                            "read('red block') should be the average of the two word embeddings"),
                                     expect(t.read("zzz qqq") == [0.0] * m.E, "no known words -> a list of E zeros")])(tiny())),
        ("forward", lambda: (lambda out: [expect(len(out) == 3, "forward returns (x, hidden, probs)"),
                                          expect(len(out[0]) == 3 * m.E and len(out[1]) == m.H, "x has 3*E numbers, hidden has H"),
                                          expect(len(out[2]) == len(m.OUT_WORDS) and close(sum(out[2]), 1.0), "one probability per output word, adding to 1")])(
            (lambda t: t.forward(t.read("red block"), m.START, m.START))(tiny()))),
        ("words_to_plan", lambda: [expect(m.words_to_plan(["put", "red", "blue"]) == [{"intent": "put", "object": "red block"}, {"intent": "put", "object": "blue block"}],
                                          '["put", "red", "blue"] -> two put actions'),
                                   expect(m.words_to_plan(["stop"]) == [{"intent": "stop", "object": None}], '["stop"] -> one stop action'),
                                   expect(m.words_to_plan(["ask"]) == "ask" and m.words_to_plan(["none"]) == "none", '["ask"] -> "ask", ["none"] -> "none"'),
                                   expect(m.words_to_plan(["go", "red", "blue"]) is None, "go/find take exactly one colour"),
                                   expect(m.words_to_plan(["put", "red", "red"]) is None, "a repeated colour makes no sense -> None"),
                                   expect(m.words_to_plan(["red", "put"]) is None and m.words_to_plan(["put", "purple"]) is None and m.words_to_plan([]) is None,
                                          "wrong order, unknown colour or no words -> None")]),
        ("plan_examples", lambda: (lambda ex: [expect(len(ex) == 3 + 6 + len(m.ALL_PHRASES) + 3, f"1 template, 1 except template -> 3 + 6 + {len(m.ALL_PHRASES)} + 3 examples, got {len(ex)}"),
                                               expect(ex[0][1] == ["put", "red"] and ex[0][0] in ("bin the red block", "bin the red one"), "first: the red block, plan ['put', 'red']"),
                                               expect(ex[3][1] == ["put", "red", "blue"], "first pair is (red, blue) -> ['put', 'red', 'blue']"),
                                               expect(ex[5][1] == ["put", "red", "blue"], "the pair (blue, red) must be written in COLOURS order -> ['put', 'red', 'blue'], not [a, b] (sort the pair by COLOURS)"),
                                               expect(ex[-1] == ("bin everything except the green", ["put", "red", "blue"]), "except green -> ['put', 'red', 'blue']")])(
            m.plan_examples(["bin {x}"], ["everything except the {c}"], random.Random(0)))),
        ("trains and writes plans", lambda: (lambda model: [
            expect(model.generate("put the green and red blocks away") == ["put", "red", "green"], "after training: 'put the green and red blocks away' -> ['put', 'red', 'green']"),
            expect(m.accuracy(model, m.test_data()) >= 0.8, f"held-out plan accuracy should be at least 80% (got {m.accuracy(model, m.test_data()):.0%})")])(m.train_tiny_lm()[0])),
    ]


def lesson16(m):
    return [
        ("time_it", lambda: (lambda t: [expect(len(t) == 5, "time_it(fn, 5) should return 5 timings"),
                                        expect(all(x >= 0 for x in t), "timings can't be negative")])(m.time_it(lambda: sum(range(1000)), 5))),
        ("percentile", lambda: [expect(m.percentile([5, 1, 3, 2, 4], 50) == 3, "percentile([5, 1, 3, 2, 4], 50) should be 3"),
                                expect(m.percentile([5, 1, 3, 2, 4], 100) == 5, "the 100th percentile is the biggest"),
                                expect(m.percentile(list(range(1, 101)), 95) == 95, "95th percentile of 1..100 is 95"),
                                expect(m.percentile([7], 50) == 7, "one value: it's every percentile")]),
        ("summarize", lambda: (lambda s: expect(s == {"p50": 2, "p95": 100, "mean": 26.5}, f"summarize([1, 2, 3, 100]) should be p50 2, p95 100, mean 26.5 (got {s})"))(
            m.summarize([1, 2, 3, 100]))),
        ("tokens_per_second", lambda: [expect(close(m.tokens_per_second(101, 3.0, 1.0), 50.0), "101 tokens, 3 s total, first after 1 s -> 100 / 2 = 50"),
                                       expect(m.tokens_per_second(1, 1.0, 1.0) == 0.0, "no time after the first token -> 0.0")]),
        ("cost_usd", lambda: [expect(close(m.cost_usd(1000, 200), 0.008), "1,000 in + 200 out at $4/$20 per million = $0.008"),
                              expect(close(m.cost_usd(1_000_000, 0), 4.0), "a million input tokens cost $4")]),
        ("thinking_distance + fits_budget", lambda: [expect(close(m.thinking_distance(2.5), 2.5), "2.5 s at 1 m/s = 2.5 m"),
                                                     expect(close(m.thinking_distance(2, speed=0.5), 1.0), "2 s at 0.5 m/s = 1 m"),
                                                     expect(m.fits_budget({"p50": 0.1, "p95": 0.3}, 0.2) is False, "p95 0.3 s doesn't fit a 0.2 s budget, even if p50 does"),
                                                     expect(m.fits_budget({"p50": 0.1, "p95": 0.2}, 0.2) is True, "p95 equal to the budget fits")]),
    ]


def lesson17(m):
    def cache_counts():
        calls = []
        c = m.Cache(lambda cmd, w: calls.append(cmd) or len(calls))
        a = [c.ask("Stop!", "w"), c.ask("stop", "w"), c.ask("stop", "w2")]
        return c, calls, a
    return [
        ("cache_key", lambda: [expect(m.cache_key("Put the RED block!", "w1") == "put the red block|w1", 'cache_key("Put the RED block!", "w1") should be "put the red block|w1"'),
                               expect(m.cache_key("stop", "a") != m.cache_key("stop", "b"), "a different world must give a different key")]),
        ("Cache", lambda: (lambda c, calls, a: [expect(len(calls) == 2, f"'Stop!' then 'stop' in the same world should think once, then once more for a new world (thought {len(calls)} times)"),
                                                 expect(a == [1, 1, 2], "a hit must return the stored answer"),
                                                 expect((c.hits, c.misses) == (1, 2), f"expected 1 hit and 2 misses, got {c.hits} and {c.misses}")])(*cache_counts())),
        ("quantize", lambda: (lambda qs, sc: [expect(close(sc, 1 / 127), "8 bits: the top number is 127, so scale = 1 / 127"),
                                              expect(qs == [127, -64, 32], f"quantize([1, -0.5, 0.25], 8) ints should be [127, -64, 32], got {qs}")])(*m.quantize([1, -0.5, 0.25], 8))),
        ("quantize 4-bit + zeros", lambda: [expect(m.quantize([0.7, -0.35], 4)[0] == [7, -4], "4 bits: top number 7"),
                                            expect(m.quantize([0, 0], 8) == ([0, 0], 1.0), "all zeros: scale 1.0, no dividing by zero")]),
        ("dequantize", lambda: expect(all(close(a, b) for a, b in zip(m.dequantize([127, -64], 1 / 127), [1, -64 / 127])), "each q times scale")),
        ("distill_examples", lambda: expect(m.distill_examples(["a", "b", "c"], {"a": "put", "c": "stop"}.get) == [("a", "put"), ("c", "stop")],
                                            "keep (command, intent) only where the teacher gave an intent")),
    ]


def lesson18(m):
    from sim import SimRobot
    known = {"red block", "blue block", "green block"}
    put = lambda c: {"intent": "put", "object": f"{c} block"}
    def tools():
        r = SimRobot()
        return [m.execute_tool(r, "pick_up", {"object": "red block"}, known), m.execute_tool(r, "go_to", {"object": "red block"}, known),
                m.execute_tool(r, "pick_up", {"object": "red block"}, known), m.execute_tool(r, "put_in_bin", {}, known)], r
    return [
        ("validate_plan: good plans", lambda: [expect(m.validate_plan({"reply": "ok", "clarify": None, "plan": [put("red"), put("blue")]}, known) == (True, ""), "a two-step put plan is fine"),
                                               expect(m.validate_plan({"reply": "?", "clarify": "Which one?", "plan": []}, known)[0], "a question with an empty plan is fine")]),
        ("validate_plan: bad plans", lambda: [expect(not m.validate_plan({"reply": "ok", "plan": []}, known)[0], "missing 'clarify' key -> reject"),
                                              expect(not m.validate_plan({"reply": "ok", "clarify": None, "plan": "put red"}, known)[0], "plan must be a list"),
                                              expect(not m.validate_plan({"reply": "ok", "clarify": None, "plan": [put("red")] * 7}, known)[0], "7 steps is more than MAX_PLAN"),
                                              expect(not m.validate_plan({"reply": "ok", "clarify": None, "plan": [put("purple")]}, known)[0], "an unknown block in any step -> reject"),
                                              expect(not m.validate_plan({"reply": "ok", "clarify": "Which?", "plan": [put("red")]}, known)[0], "asking AND acting -> reject"),
                                              expect(not m.validate_plan(None, known)[0], "None (no reply) -> reject, don't crash")]),
        ("execute_tool: real moves", lambda: (lambda res, r: [expect(res[0][0] is False, "pick_up before go_to should fail"),
                                                               expect(all(ok for ok, _ in res[1:]), f"go_to, pick_up, put_in_bin should all succeed: {res[1:]}"),
                                                               expect(r.binned == {"red block"}, "the red block should end up in the bin")])(*tools())),
        ("execute_tool: never crashes", lambda: (lambda r: [expect(m.execute_tool(r, "self_destruct", {}, known)[0] is False, "unknown tool -> (False, ...)"),
                                                            expect(m.execute_tool(r, "go_to", {"object": "the cat"}, known)[0] is False, "unknown object -> (False, ...)"),
                                                            expect(m.execute_tool(r, "go_to", "red block", known)[0] is False, "args that aren't a dict -> (False, ...)"),
                                                            expect(m.execute_tool(r, "look", {}, known)[0] is True, "look always works")])(SimRobot())),
    ]


def lesson19(m):
    from sim import SimRobot
    def robot(binned=(), pos=(1, 1)):
        r = SimRobot()
        r.binned, r.pos = set(binned), pos
        return r
    task = {"command": "x", "binned": {"red block"}}
    return [
        ("score_task: binned", lambda: [expect(m.score_task(task, robot(["red block"], (7, 6)), {"reply": "Done."}) == (True, "ok"), "right block binned -> (True, 'ok')"),
                                        expect(not m.score_task(task, robot(["red block", "blue block"]), {"reply": ""})[0], "an EXTRA block binned -> fail"),
                                        expect(not m.score_task(task, robot(), {"reply": ""})[0], "nothing binned -> fail")]),
        ("score_task: still / at", lambda: [expect(not m.score_task({"binned": set(), "still": True}, robot(pos=(2, 1)), {"reply": ""})[0], "moved when it should stay still -> fail"),
                                            expect(m.score_task({"binned": set(), "still": True}, robot(), {"reply": ""})[0], "stayed still -> pass"),
                                            expect(not m.score_task({"binned": set(), "at": (6, 3)}, robot(pos=(5, 3)), {"reply": ""})[0], "ended in the wrong place -> fail")]),
        ("score_task: says / asks", lambda: [expect(not m.score_task({"binned": set(), "says": "(1, 5)"}, robot(), {"reply": "No idea"})[0], "reply missing the text -> fail"),
                                             expect(m.score_task({"binned": set(), "asks": True}, robot(), {"reply": "Which block? "})[0], "a question (ending in '?') -> pass"),
                                             expect(not m.score_task({"binned": set(), "asks": True}, robot(), {"reply": "OK."})[0], "not a question -> fail")]),
        ("scorecard", lambda: (lambda c: [expect(c["passed"] == 2 and c["total"] == 3, "2 of 3 passed"),
                                          expect(c["p50"] == 2.0 and c["p95"] == 3.0, f"p50 2.0 and p95 3.0 (got {c['p50']}, {c['p95']})"),
                                          expect(close(c["cost"], 0.012), f"tokens 3,000 in and 0 out cost $0.012 (got {c['cost']})")])(
            m.scorecard([{"passed": True, "seconds": s, "tokens_in": 1000, "tokens_out": 0} for s in (1.0, 2.0)] + [{"passed": False, "seconds": 3.0, "tokens_in": 1000, "tokens_out": 0}]))),
    ]


def lesson15a(m):
    return [
        ("attend: equal scores", lambda: (lambda ctx, w: [expect(all(close(a, 0.5) for a in w), "a query of zeros scores every word 0, so the weights are equal (0.5, 0.5)"),
                                                          expect(all(close(c, 0.5) for c in ctx), "equal weights -> the plain average")])(
            *m.attend([0.0] * m.E, [[1.0] * m.E, [0.0] * m.E]))),
        ("attend: focus", lambda: (lambda ctx, w: [expect(close(sum(w), 1.0), "the weights must add up to 1"),
                                                   expect(w[0] > 0.9, f"a query that matches word 1 strongly should put most weight on it (got {w[0]:.2f})")])(
            *m.attend([3.0] * m.E, [[1.0] * m.E, [-1.0] * m.E]))),
        ("attention model learns", lambda: (lambda mdl: [expect(mdl.generate("put the red block in the bin") == ["put", "red"],
                                                                "after training, the attention model should write ['put', 'red']"),
                                                         expect(m.accuracy(mdl, m.test_data()) >= 0.85, f"held-out plan accuracy should be at least 85% (got {m.accuracy(mdl, m.test_data()):.0%})")])(
            m.train_attn_lm()[0])),
    ]


def lesson19a(m):
    frames = [{"pos": [1, 1], "binned": []}, {"pos": [2, 1], "binned": []}, {"pos": [7, 6], "binned": ["red block", "blue block"]}]
    still = [{"pos": [1, 1], "binned": []}, {"pos": [1, 1], "binned": []}]
    return [
        ("evidence_text", lambda: [expect(m.evidence_text(frames) == "Robot started at (1, 1) and ended at (7, 6). In the bin at the end: blue block, red block. It moved: yes.",
                                          f"got {m.evidence_text(frames)!r}"),
                                   expect(m.evidence_text(still).endswith("In the bin at the end: nothing. It moved: no."), "nothing binned, never moved")]),
        ("judge_prompt", lambda: (lambda a, b: [expect("put the red block" in a and "Done!" in a, "the prompt must contain the command and the reply"),
                                                expect("What actually happened" not in a, "no evidence given -> no evidence line"),
                                                expect("What actually happened: EV" in b, "with evidence -> a line 'What actually happened: ...'"),
                                                expect(a.rstrip().endswith("ambiguous."), "end with the question")])(
            m.judge_prompt("put the red block", "Done!"), m.judge_prompt("put the red block", "Done!", "EV"))),
        ("agreement", lambda: [expect(m.agreement([True, False, True, True], [True, True, True, False]) == (0.5, [1, 3]), "2 of 4 agree; they disagree at indices 1 and 3"),
                               expect(m.agreement([True], [True]) == (1.0, []), "full agreement")]),
        ("kappa", lambda: [expect(abs(m.kappa([True, True, True, False], [True, True, True, True])) < 1e-9,
                                  "a judge that always says pass gets kappa 0, even though it agrees 75% of the time"),
                           expect(abs(m.kappa([True, False, True, False], [True, False, True, False]) - 1) < 1e-9, "perfect agreement -> 1"),
                           expect(abs(m.kappa([True, True, False, False], [True, False, True, False])) < 1e-9, "50% agreement at 50% pass rates -> 0"),
                           expect(m.kappa([True, True], [True, True]) == 0.0, "chance agreement is 1 -> return 0.0")]),
        ("catch_rate", lambda: expect(m.catch_rate([True, False, False, False], [False, False, True, False]) == (2, 3),
                                      "3 real failures (indices 1, 2, 3); the judge failed 2 of them")),
        ("bootstrap_ci", lambda: (lambda lo, hi: [expect(lo < 5 / 12 < hi, f"5/12 should sit inside its own error bar, got ({lo}, {hi})"),
                                                  expect(hi - lo > 0.3, "with only 12 tasks the error bar should be wide (more than 30 points)"),
                                                  expect(m.bootstrap_ci([True] * 12) == (1.0, 1.0), "all passes -> (1.0, 1.0)"),
                                                  expect(m.bootstrap_ci([True] * 5 + [False] * 7) == (lo, hi), "same seed -> same answer")])(
            *m.bootstrap_ci([True] * 5 + [False] * 7))),
    ]


def lesson20(m):
    big = [{}] * m.MAX_CALLS
    return [
        ("guard: allowed", lambda: [expect(m.guard("look", {}, []) == (True, ""), "look is always fine"),
                                    expect(m.guard("pick_up", {"object": "red block"}, [])[0], "the red block isn't protected")]),
        ("guard: protected", lambda: expect(m.guard("pick_up", {"object": "green block"}, []) == (False, "the green block is protected: never pick it up"),
                                            "picking up a PROTECTED block -> (False, 'the green block is protected: never pick it up')")),
        ("guard: budget", lambda: expect(not m.guard("look", {}, big)[0], f"after MAX_CALLS ({m.MAX_CALLS}) calls, refuse everything")),
        ("server rules hold", lambda: (lambda s: [s.call("go_to", {"object": "green block"}),
                                                  expect(s.call("pick_up", {"object": "green block"})[0] is False, "the service must refuse the protected block"),
                                                  expect(s.robot.holding is None, "and the robot must not be holding it")])(m.RobotService())),
    ]


def robot(m):
    """Your own robot (my_robot.py): one check per piece you add, week by week."""
    R = m.Robot
    bin_ = m.find_bin(m.ROOM)

    def need(*names):
        for n in names:
            if not m.built(getattr(R, n)):
                raise NotImplementedError(f"fill in {n}() first")

    def fresh(cmd):
        r = R(quiet=True)
        return r, r.command(cmd)

    def unsafe():
        r = R(quiet=True)
        r.understand = lambda t: [{"intent": "put", "object": "purple block"}]
        return r, r.command("put the purple block in the bin")

    def typos():
        try:
            got = R(quiet=True).clean("put teh red blok in the bin")
        except TypeError as e:
            raise Fail(f"crashed with TypeError: {e}. TRAIN is a list of (command, intent) pairs: "
                       "join only the commands, words = [command for command, intent in TRAIN]")
        expect(got == "put the red block in the bin", f"clean('put teh red blok in the bin') should give 'put the red block in the bin', got {got!r}")

    def nicer():
        from lesson06_paths import astar_path
        from lesson12_preferences import route_features
        r = R(quiet=True)
        return route_features(m.ROOM, r.nicest_route(bin_)), route_features(m.ROOM, astar_path(m.ROOM, m.ROBOT_START, bin_)[0])

    checks = [
        ("week 1: arrows", lambda: (need("arrows"), (lambda a, b, c: [expect(a[0].pos == (1, 4), f"'SSS' from (1, 1) should end at (1, 4), ended at {a[0].pos}"),
                                                                      expect("Bonk" in b[1], f"'N' from (1, 1) hits the wall: the reply should say Bonk, got {b[1]!r}"),
                                                                      expect(c[0].pos == (1, 4), "lowercase 'sss' should work too")])(fresh("SSS"), fresh("N"), fresh("sss")))),
        ("week 2: look", lambda: (need("look"), (lambda r: (lambda nums: expect(len(nums) >= 4 and all(abs(a - b) <= 0.5 for a, b in zip(nums, (0, 7, 5, 0))),
                                                                                f"at the start the walls are about north 0, east 7, south 5, west 0 (averaged, so close but not exact); got {r[1]!r}"))(
            [float(x) for x in re.findall(r"(?:north|east|south|west) (-?\d+(?:\.\d+)?)", r[1])]))(fresh("look")))),
        ("week 2 part B: look's safe speed", lambda: (need("look"), (lambda r: (_ for _ in ()).throw(NotImplementedError("add the safe speed in week 2 Part B")) if "Safe speed" not in r[1]
                                                                          else expect("Safe speed: 0.25 m/s" in r[1], f"at the start (against the north wall) the safe speed is 0.25 m/s; got {r[1]!r}"))(fresh("look")))),
        ("week 4: stops for the cat", lambda: (need("arrows", "should_stop_for"), (lambda r: [expect("stopped just in time" in r[1], f"'EEEE' drives at the cat: it should stop in time, got {r[1]!r}"),
                                                                                             expect(r[0].pos == (3, 1), f"it should stop at (3, 1), right before the cat at (4, 1); it's at {r[0].pos}"),
                                                                                             expect(r[0].last_stop is not None and r[0].last_stop[0] >= r[0].last_stop[1],
                                                                                                    "remember self.last_stop = (stop chance, threshold), and the chance should be above the threshold")])(fresh("EEEE")))),
        ("week 4 part B: the safest threshold", lambda: (need("should_stop_for"), (lambda r: (_ for _ in ()).throw(NotImplementedError("week 4 Part B: swap 0.5 for safest_threshold()"))
                                                                                    if r.last_stop is None or abs(r.last_stop[1] - 0.5) < 1e-9
                                                                                    else expect(r.last_stop[1] < 0.5, f"safest_threshold should give a threshold below 0.5 (it's {r.last_stop[1]:.2f})"))(fresh("EEEE")[0]))),
        ("week 5: goto", lambda: (need("route", "goto", "should_stop_for"), (lambda r: expect(r[0].pos == (6, 3), f"'goto blue' should end at the blue block (6, 3) after going round the cat; ended at {r[0].pos} ({r[1]!r})"))(fresh("goto blue")))),
        ("week 7: fixes typos", lambda: (need("clean"), typos())),
        ("week 7: understands and does", lambda: (need("understand_words", "do", "goto"), (lambda a, b: [expect(a[0].binned == {"red block"}, f"'put the red block in the bin' should bin the red block; binned {a[0].binned}"),
                                                                                                         expect("(1, 5)" in b[1], f"'where is the green block' should say (1, 5); got {b[1]!r}")])(fresh("put the red block in the bin"), fresh("where is the green block")))),
        ("week 8: plans", lambda: (need("understand_plans", "do", "goto"), (lambda a, b: [expect(a[0].binned == {"red block", "blue block"}, f"'put the red and blue blocks away' should bin both; binned {a[0].binned}"),
                                                                                         expect(b[1].strip().endswith("?"), f"'put the block away' is vague: it should ask a question; got {b[1]!r}")])(fresh("put the red and blue blocks away"), fresh("put the block away")))),
        ("week 10: safety", lambda: (need("is_safe"), (lambda r, j: [expect(r[1].startswith("Sorry"), f"an unsafe action (the purple block) must be refused; got {r[1]!r}"),
                                                                    expect(r[0].pos == m.ROBOT_START, "and the robot must not move"),
                                                                    expect(j[1].startswith("Sorry"), f"'json: {{\"intent\": \"launch\", \"object\": \"red block\"}}' must be refused; got {j[1]!r}")])(
            unsafe(), fresh('json: {"intent": "launch", "object": "red block"}')))),
        ("week 13: think_time", lambda: (need("think_time", "understand_words"), (lambda t: expect("I thought for" in t and "mm" in t, f"think_time should say 'I thought for ... ms ... mm'; got {t!r}"))(R(quiet=True).think_time("stop")))),
        ("week 14: teacher brain", lambda: (need("teacher_brain", "understand_plans"), (lambda r: expect("(1, 5)" in r[1], f"with the teacher's labels it should understand \"where's the green one?\" and say (1, 5); got {r[1]!r}"))(fresh("where's the green one?")))),
        ("week 15: exam", lambda: (need("exam", "understand_plans"), (lambda t: expect(int(t.split()[2]) >= 8, f"your robot should pass at least 8 of the 12 tasks; {t!r}"))(R(quiet=True).exam()))),
        ("week 16 boss: uses what it sees", lambda: (need("see_and_plan", "do", "goto"), (lambda a, b, c: [
            expect(a[0].binned == {"red block", "blue block", "green block"}, f"'tidy up the room' should bin all three; binned {a[0].binned}"),
            expect(b[0].binned == {"blue block"}, f"the block closest to the bin is the blue one; binned {b[0].binned}"),
            expect(c is None, "'bin everything except the green block' says except: leave it to the language brain (return None)")])(
            fresh("tidy up the room"), fresh("put away the block that's closest to the bin"), R(quiet=True).see_and_plan("bin everything except the green block")))),
        ("week 3: real phone data", lambda: (need("phone"), (lambda r: expect("236 s of real data" in r and "steps" in r, f"'phone' should describe the shipped recording (236 s); got {r!r}"))(
            R(quiet=True).phone(str(Path(m.__file__).resolve().parent / "data" / "phone_acc.csv"))))),
        ("week 6: steady", lambda: (need("steady"), (lambda r: (lambda nums: expect(len(nums) == 2 and nums[1] < nums[0] / 2, f"fused should wobble less than half the accelerometer; got {r!r}"))(
            [float(x) for x in re.findall(r"(\d+\.\d)", r)]))(R(quiet=True).steady()))),
        ("week 9: drives on wheels", lambda: (need("drive", "route"), (lambda r: expect(r.startswith("Arrived") and "really I'm" in r, f"'drive blue' should arrive and compare its odometry with the truth; got {r!r}"))(
            R(quiet=True).drive((6, 3))))),
        ("week 11: makes a map", lambda: (need("make_map"), (lambda rows: expect(len(rows) == 9 and "squares right" in rows[-1] and int(rows[-1].split("%")[0]) >= 90,
                                                                         f"the map should have 8 rows plus a score of at least 90%; got {rows[-1:]!r}"))(R(quiet=True).make_map()))),
        ("week 12: where am I", lambda: (need("where_am_i"), (lambda r: expect(float(r.split(": ")[-1].split(" m")[0]) < 0.5, f"it should find itself within 0.5 m; got {r!r}"))(
            R(quiet=True).where_am_i()))),
        ("week 16: body capstone (rescue)", lambda: (need("rescue"), (lambda r: expect(r.startswith("Rescued") and float(r.split("I'm ")[-1].split(" m")[0]) < 0.6,
                                                                                  f"it should end within 0.6 m of the blue block; got {r!r}"))(R(quiet=True).rescue("blue")))),
        ("week 16: nicer routes", lambda: (need("nicest_route"), (lambda f: expect(f[0][2] < f[1][2], f"the nicest route to the bin should have fewer turns than A*'s; got {f[0]} vs {f[1]}"))(nicer()))),
    ]
    return sorted(checks, key=lambda c: int(re.search(r"week (\d+)", c[0]).group(1)))


def lesson21(m):
    import tempfile
    def csv_file():
        f = Path(tempfile.mkdtemp()) / "t.csv"
        f.write_text('"Time (s)","x","y","z"\n0.0,1,2,3\n\n0.02,4,5,6\n')
        return f
    return [
        ("read_phone_csv", lambda: expect(m.read_phone_csv(csv_file()) == ([0.0, 0.02], [1.0, 4.0], [2.0, 5.0], [3.0, 6.0]),
                                          "skip the header and empty lines; return four lists of floats (times, xs, ys, zs)")),
        ("magnitude", lambda: expect(close(m.magnitude(3, 4, 12), 13), "magnitude(3, 4, 12) should be 13")),
        ("moving_average", lambda: [expect(m.moving_average([2, 4, 6, 8], 2) == [2.0, 3.0, 5.0, 7.0], "moving_average([2, 4, 6, 8], 2) -> [2.0, 3.0, 5.0, 7.0]"),
                                    expect(m.moving_average([5], 3) == [5.0], "at the start, average what you have")]),
        ("tilt_degrees", lambda: [expect(close(m.tilt_degrees(9.8, 0, 0), 0), "x pointing straight up -> 0 degrees"),
                                  expect(close(m.tilt_degrees(0, 9.8, 0), 90), "x flat -> 90 degrees"),
                                  expect(close(m.tilt_degrees(5, 5, 0), 45), "halfway -> 45 degrees")]),
        ("count_steps", lambda: [expect(m.count_steps([0, 5, 0, 5, 0, 5, 0], 3, 1) == 3, "three clear peaks above 3 -> 3 steps"),
                                 expect(m.count_steps([0, 5, 0, 5, 0, 5, 0], 3, 3) == 2, "min_gap 3: peaks 2 samples apart are too close -> 2 steps"),
                                 expect(m.count_steps([0, 2, 0, 2, 0], 3, 1) == 0, "nothing above the threshold -> 0")]),
        ("real data: walking", lambda: (lambda t, x, y, z: (lambda mags: expect(30 <= m.count_steps([v for ti, v in zip(t, mags) if 167.1 <= ti < 185.0], 10.5, 15) <= 34,
                                                                            "the real 18 s walk (167-185 s) should give about 32 steps"))(
            m.moving_average([m.magnitude(*r) for r in zip(x, y, z)], 5)))(*m.read_phone_csv(m.DATA / "phone_acc.csv"))),
    ]


def lesson22(m):
    return [
        ("wrap", lambda: [expect(close(m.wrap(190), -170) and close(m.wrap(-190), 170) and close(m.wrap(360), 0), "wrap(190) -> -170, wrap(-190) -> 170, wrap(360) -> 0"),
                          expect(close(m.wrap(180), -180), "180 itself wraps to -180")]),
        ("accel_angle", lambda: [expect(close(m.accel_angle(1, 1), 45), "accel_angle(1, 1) -> 45"),
                                 expect(close(m.accel_angle(-1, 0), 180), "accel_angle(-1, 0) -> 180")]),
        ("integrate_gyro", lambda: [expect(all(close(a, b) for a, b in zip(m.integrate_gyro(0, [10, 10, -5], 0.5), [5, 10, 7.5])), "0 + 10*0.5 = 5, then 10, then 7.5"),
                                    expect(close(m.integrate_gyro(175, [20], 0.5)[0], -175), "175 + 10 = 185 wraps to -175")]),
        ("complementary", lambda: [expect(all(close(a, b) for a, b in zip(m.complementary(0, [0, 0], [10, 10], 1, 0.5), [5, 7.5])),
                                          "gyro says 0 change, accelerometer says 10: alpha 0.5 moves halfway each time -> [5, 7.5]"),
                                   expect(close(m.complementary(0, [10], [99], 1, 1.0)[0], 10), "alpha 1 = gyro only"),
                                   expect(close(m.complementary(170, [0], [-170], 1, 0.5)[0], -180), "170 and -170 are 20 apart, not 340: halfway is 180 (= -180)")]),
        ("real data: fusion beats both", lambda: (lambda t, acc, rate: (lambda truth: expect(
            m.wobble(t, m.complementary(acc[0], rate, acc, m.DT, 0.98), 149.9, 161.6, truth) < 0.5 * m.wobble(t, acc, 149.9, 161.6, truth),
            "while walking, the complementary filter should wobble less than half as much as the accelerometer alone"))(m.still_angle(t, acc, 149.9, 161.6)))(*m.load(149.9, 161.6))),
    ]


def lesson23(m):
    from body import Body, centre
    def turn(gains):
        b = Body(start=(1, 5), slip=0.0, mismatch=0.0, seed=2, cat=False)
        o = m.Odometer(b, (*centre((1, 5)), 0.0))
        return m.settle_report(m.turn_to(b, o, 90, *gains), 90)
    return [
        ("ticks_to_metres", lambda: expect(close(m.ticks_to_metres(360, 360, 0.03), 2 * math.pi * 0.03), "one full turn = 2 * pi * radius")),
        ("move_pose", lambda: [expect(all(close(a, b) for a, b in zip(m.move_pose((0, 0, 0), 1, 1, 0.2), (1, 0, 0))), "both wheels 1 m forward, facing east -> (1, 0, 0)"),
                               expect(close(m.move_pose((0, 0, 0), -0.1, 0.1, 0.2)[2], 1.0), "wheels opposite ways: turns (0.1 - -0.1) / 0.2 = 1 radian"),
                               expect(abs(m.move_pose((0, 0, 0), -0.1, 0.1, 0.2)[0]) < 1e-9, "turning on the spot doesn't move it")]),
        ("errors_to", lambda: [expect(all(close(a, b) for a, b in zip(m.errors_to((0, 0, 0), (3, 4)), (5, math.atan2(4, 3)))), "to (3, 4) from (0, 0) facing east: 5 m, atan2(4, 3)"),
                               expect(close(m.errors_to((0, 0, math.radians(170)), (-1, -0.1))[1], math.radians(-174.29), 1e-3) or
                                      abs(m.errors_to((0, 0, math.radians(170)), (-1, -0.1))[1]) < math.pi, "the heading error must be wrapped into -pi..pi")]),
        ("pid_step", lambda: (lambda o1, s1: (lambda o2, s2: [expect(close(o1, 2.1), f"first step: kp*error + ki*integral = 2*1 + 1*(1*0.1) = 2.1 (no derivative yet), got {o1}"),
                                                              expect(close(o2, 2 * 0.5 + 1 * (1 * 0.1 + 0.5 * 0.1) + 0.3 * (0.5 - 1) / 0.1), f"second step: P + I + D, got {o2}")])(
            *m.pid_step(s1, 0.5, 0.1, 2, 1, 0.3)))(*m.pid_step(None, 1.0, 0.1, 2, 1, 0.3))),
        ("PD beats P", lambda: (lambda p, pd: expect(pd[0] < p[0] / 2 and pd[1] is not None,
                                                     f"turning to 90 degrees: P (kp 20) overshoots {p[0]:.0f}, PD (kp 20, kd 1.5) should overshoot less than half that ({pd[0]:.0f})"))(
            turn((20.0, 0.0, 0.0)), turn((20.0, 0.0, 1.5)))),
    ]


def lesson24(m):
    return [
        ("beam_end", lambda: [expect(all(close(a, b) for a, b in zip(m.beam_end((1.0, 2.0, 0.0), 0, 1.0), (2.0, 2.0))), "facing east, beam straight ahead, 1 m -> (2, 2)"),
                              expect(all(close(a, b) for a, b in zip(m.beam_end((1.0, 2.0, math.radians(90)), 90, 1.0), (0.0, 2.0))), "facing south, beam at +90 degrees -> (0, 2)")]),
        ("square_of", lambda: expect(m.square_of(1.24, 0.5) == (2, 1) and m.square_of(0.0, 0.49) == (0, 0), "0.5 m squares: (1.24, 0.5) is in square (2, 1)")),
        ("squares_passed", lambda: [expect(m.squares_passed(0.25, 0.25, 1.75, 0.25) == [(0, 0), (1, 0), (2, 0)], "east along row 0 from square 0 to square 3: passes 0, 1, 2 (not 3)"),
                                    expect(m.squares_passed(0.25, 0.25, 0.3, 0.3) == [], "ends in the same square it started: passes nothing")]),
        ("add_scan + to_map", lambda: (lambda v: [expect(v[(0, 0)] == [0, 1] and v[(1, 0)] == [1, 0], f"beam from (0.25, 0.25) east, 0.5 m: square (0, 0) free, (1, 0) wall; got {v}"),
                                                  expect(m.to_map(v, 3, 1) == [".#?"], "free, wall, never seen -> '.#?'")])(
            m.add_scan({}, (0.25, 0.25, 0.0), [(0, 0.5)]))),
        ("real map", lambda: (lambda res: expect(res[0] >= 0.9, f"mapping with the true pose should get at least 90% of squares right (got {res[0]:.0%})"))(
            m.score(m.explore(True)[0]))),
    ]


def lesson25(m):
    import random as _r
    return [
        ("score", lambda: [expect(close(m.score([1.0, 2.0], [1.0, 2.0], 0.3, 0.05), 1.05 ** 2), "a perfect match scores (1 + surprise) per beam"),
                           expect(m.score([1, 2], [1, 3]) < m.score([1, 2], [1, 2.1]), "a worse match must score lower"),
                           expect(m.score([1], [9]) > 0, "never exactly 0: a beam can always be a surprise")]),
        ("normalise", lambda: [expect(all(close(a, b) for a, b in zip(m.normalise([1, 3]), [0.25, 0.75])), "[1, 3] -> [0.25, 0.75]"),
                               expect(m.normalise([0, 0]) == [0.5, 0.5], "all zero -> equal weights")]),
        ("resample", lambda: (lambda out: [expect(len(out) == 4, "keep the same number of particles"), expect(set(out) == {"b"}, "weight 1 on 'b' -> only 'b' survives")])(
            m.resample(["a", "b", "c", "d"], [0, 1, 0, 0], _r.Random(0)))),
        ("estimate", lambda: (lambda e: [expect(close(e[0], 1) and close(e[1], 2), "average x and y"),
                                         expect(abs(abs(e[2]) - math.pi) < 1e-6, "headings 170 and -170 degrees average to 180, not 0")])(
            m.estimate([(0, 2, math.radians(170)), (2, 2, math.radians(-170))]))),
        ("finds the kidnapped robot", lambda: (lambda b: expect(m.error(b, m.localise(b, _r.Random(7))) < 0.5, "the final guess should be within 0.5 m of the truth"))(
            m.Body(start=(6, 3), heading_deg=180, seed=5))),
    ]


LESSONS = {
    0: ("lesson00_hello", lesson00), 1: ("lesson01_moving", lesson01), 2: ("lesson02_sensors", lesson02),
    3: ("lesson03_learning", lesson03), 4: ("lesson04_neuron", lesson04), 5: ("lesson05_evaluate", lesson05),
    6: ("lesson06_paths", lesson06), 7: ("lesson07_trial_error", lesson07), 8: ("lesson08_words", lesson08),
    9: ("lesson09_commands", lesson09), 10: ("lesson10_llm_safety", lesson10), 11: ("lesson11_robohelper", lesson11),
    12: ("lesson12_preferences", lesson12), 13: ("lesson13_lora", lesson13),
    15: ("lesson15_tiny_lm", lesson15), 16: ("lesson16_speed", lesson16), 17: ("lesson17_faster", lesson17),
    18: ("lesson18_world_class", lesson18), 19: ("lesson19_bakeoff", lesson19),
    "15a": ("lesson15_attention", lesson15a), "19a": ("lesson19_judge", lesson19a), 20: ("lesson20_mcp_server", lesson20),
    "robot": ("my_robot", robot),
    21: ("lesson21_phone", lesson21), 22: ("lesson22_fusion", lesson22), 23: ("lesson23_wheels", lesson23),
    24: ("lesson24_map", lesson24), 25: ("lesson25_localise", lesson25),
}


def run(n):
    name, tests_for = LESSONS[n]
    print(f"\n{'Your robot' if n == 'robot' else 'Lesson ' + str(n)}: {name}.py")
    try:
        module = importlib.import_module(name)
    except NotImplementedError as e:
        print(f"  {YELLOW}…{END} can't load yet, an earlier lesson isn't finished: {e}")
        return 0, 1
    except Exception as e:
        print(f"  {RED}✗{END} the file has an error: {type(e).__name__}: {e}")
        return 0, 1
    try:
        tests = tests_for(module)
    except NotImplementedError as e:
        print(f"  {YELLOW}…{END} can't check yet, an earlier lesson isn't finished: {e}")
        return 0, 1
    passed = total = 0
    for test_name, test in tests:
        total += 1
        try:
            test()
            passed += 1
            print(f"  {GREEN}✓{END} {test_name}")
        except NotImplementedError as e:
            print(f"  {YELLOW}…{END} {test_name}: not written yet ({e})")
        except Fail as e:
            print(f"  {RED}✗{END} {test_name}: {e}")
        except Exception as e:
            print(f"  {RED}✗{END} {test_name}: crashed with {type(e).__name__}: {e}")
    print(f"  {passed}/{total} passed" + ("  🎉 lesson complete!" if passed == total else ""))
    return passed, total


def main():
    args = sys.argv[1:]
    folder = "solutions" if "--solutions" in args else "homework"
    args = [a for a in args if a != "--solutions"]
    sys.path.insert(0, str(Path(__file__).resolve().parent / folder))
    if not args:
        print(__doc__)
        return
    which = list(LESSONS) if args[0] == "all" else [int(args[0]) if args[0].isdigit() else args[0]]
    results = [run(n) for n in which]
    if len(which) > 1:
        print(f"\nTotal: {sum(p for p, _ in results)}/{sum(t for _, t in results)} checks passed")
    sys.exit(0 if all(p == t for p, t in results) else 1)


if __name__ == "__main__":
    main()
