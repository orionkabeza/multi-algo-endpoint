import shutil
import tempfile
import unittest
from pathlib import Path

import visualizer
from algorithms import (
    ALGORITHMS,
    balanced_parentheses,
    balanced_setup,
    bfs_traversal,
    graph_setup,
    hanoi_setup,
    naive_queue_enqueue_dequeue,
    next_greater_elements,
    queue_enqueue_dequeue,
    queue_setup,
    stack_push_pop,
    stack_setup,
    tower_of_hanoi,
)
from stack_queue import NaiveQueue, Queue, QueueEmptyError, Stack, StackEmptyError


class StackTests(unittest.TestCase):
    def test_push_pop_is_lifo(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)

    def test_peek_does_not_remove(self):
        s = Stack()
        s.push("a")
        s.push("b")
        self.assertEqual(s.peek(), "b")
        self.assertEqual(len(s), 2)

    def test_is_empty_and_bool(self):
        s = Stack()
        self.assertTrue(s.is_empty())
        self.assertFalse(bool(s))
        s.push(1)
        self.assertFalse(s.is_empty())
        self.assertTrue(bool(s))

    def test_len(self):
        s = Stack()
        for i in range(5):
            s.push(i)
        self.assertEqual(len(s), 5)

    def test_pop_from_empty_raises(self):
        s = Stack()
        with self.assertRaises(StackEmptyError):
            s.pop()
        with self.assertRaises(IndexError):
            Stack().pop()

    def test_peek_at_empty_raises(self):
        with self.assertRaises(StackEmptyError):
            Stack().peek()

    def test_none_as_value(self):
        s = Stack()
        s.push(None)
        self.assertFalse(s.is_empty())
        self.assertIsNone(s.pop())
        self.assertTrue(s.is_empty())

    def test_refill_after_emptying(self):
        s = Stack()
        s.push(1)
        s.pop()
        self.assertTrue(s.is_empty())
        s.push(2)
        s.push(3)
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 2)

    def test_iteration_order_is_top_to_bottom(self):
        s = Stack()
        for i in [1, 2, 3]:
            s.push(i)
        self.assertEqual(list(s), [3, 2, 1])


class QueueTests(unittest.TestCase):
    def test_enqueue_dequeue_is_fifo(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(q.dequeue(), 1)
        self.assertEqual(q.dequeue(), 2)
        self.assertEqual(q.dequeue(), 3)

    def test_peek_does_not_remove(self):
        q = Queue()
        q.enqueue("a")
        q.enqueue("b")
        self.assertEqual(q.peek(), "a")
        self.assertEqual(len(q), 2)

    def test_is_empty_and_bool(self):
        q = Queue()
        self.assertTrue(q.is_empty())
        self.assertFalse(bool(q))
        q.enqueue(1)
        self.assertFalse(q.is_empty())
        self.assertTrue(bool(q))

    def test_len(self):
        q = Queue()
        for i in range(5):
            q.enqueue(i)
        self.assertEqual(len(q), 5)

    def test_dequeue_from_empty_raises(self):
        q = Queue()
        with self.assertRaises(QueueEmptyError):
            q.dequeue()
        with self.assertRaises(IndexError):
            Queue().dequeue()

    def test_peek_at_empty_raises(self):
        with self.assertRaises(QueueEmptyError):
            Queue().peek()

    def test_none_as_value(self):
        q = Queue()
        q.enqueue(None)
        self.assertFalse(q.is_empty())
        self.assertIsNone(q.dequeue())
        self.assertTrue(q.is_empty())

    def test_refill_after_emptying(self):
        q = Queue()
        q.enqueue(1)
        q.dequeue()
        self.assertTrue(q.is_empty())
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(q.dequeue(), 2)
        self.assertEqual(q.dequeue(), 3)

    def test_iteration_order_is_front_to_back(self):
        q = Queue()
        for i in [1, 2, 3]:
            q.enqueue(i)
        self.assertEqual(list(q), [1, 2, 3])


class NaiveQueueTests(unittest.TestCase):
    def test_matches_queue_output(self):
        items = list(range(50))
        naive = NaiveQueue()
        real = Queue()
        for item in items:
            naive.enqueue(item)
            real.enqueue(item)
        naive_out = [naive.dequeue() for _ in items]
        real_out = [real.dequeue() for _ in items]
        self.assertEqual(naive_out, real_out)

    def test_dequeue_from_empty_raises(self):
        with self.assertRaises(QueueEmptyError):
            NaiveQueue().dequeue()


class StackQueueAlgorithmCorrectnessTests(unittest.TestCase):
    def test_stack_push_pop_reverses_input(self):
        data = stack_setup(20)
        self.assertEqual(stack_push_pop(data), list(reversed(data)))

    def test_queue_enqueue_dequeue_preserves_order(self):
        data = queue_setup(20)
        self.assertEqual(queue_enqueue_dequeue(data), data)

    def test_naive_queue_matches_deque_queue(self):
        data = queue_setup(20)
        self.assertEqual(naive_queue_enqueue_dequeue(data), queue_enqueue_dequeue(data))

    def test_balanced_parentheses_true_cases(self):
        self.assertTrue(balanced_parentheses(""))
        self.assertTrue(balanced_parentheses("()"))
        self.assertTrue(balanced_parentheses(balanced_setup(5)))
        self.assertTrue(balanced_parentheses("(a)"))     # non-bracket chars are ignored
        self.assertTrue(balanced_parentheses("a"))
        self.assertTrue(balanced_parentheses("([]{})"))  # mixed bracket types

    def test_balanced_parentheses_false_cases(self):
        self.assertFalse(balanced_parentheses("("))
        self.assertFalse(balanced_parentheses(")"))
        self.assertFalse(balanced_parentheses(")("))
        self.assertFalse(balanced_parentheses("(()"))
        self.assertFalse(balanced_parentheses("([)]"))   # wrong nesting order

    def test_next_greater_elements_known_example(self):
        self.assertEqual(next_greater_elements([2, 1, 2, 4, 3]), [4, 2, 4, -1, -1])

    def test_next_greater_elements_all_decreasing(self):
        self.assertEqual(next_greater_elements([5, 4, 3, 2, 1]), [-1, -1, -1, -1, -1])

    def test_bfs_traversal_visits_path_graph_in_order(self):
        graph = graph_setup(6)
        self.assertEqual(bfs_traversal(graph), [0, 1, 2, 3, 4, 5])

    def test_bfs_traversal_empty_graph(self):
        self.assertEqual(bfs_traversal({}), [])

    def test_tower_of_hanoi_move_count(self):
        for n in [0, 1, 2, 3, 8]:
            self.assertEqual(tower_of_hanoi(n), 2 ** n - 1)


class VisualizerIntegrationTests(unittest.TestCase):
    NEW_ALGOS = [
        "stack_push_pop",
        "queue_enqueue_dequeue",
        "naive_queue_enqueue_dequeue",
        "balanced_parentheses",
        "next_greater_elements",
        "bfs_traversal",
        "tower_of_hanoi",
    ]

    def setUp(self):
        self._real_snapshot_dir = visualizer.SNAPSHOT_DIR
        visualizer.SNAPSHOT_DIR = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(visualizer.SNAPSHOT_DIR, ignore_errors=True)
        visualizer.SNAPSHOT_DIR = self._real_snapshot_dir

    def test_new_algorithms_are_registered(self):
        for name in self.NEW_ALGOS:
            self.assertIn(name, ALGORITHMS)

    def test_measure_runs_for_each_new_algorithm(self):
        for name in self.NEW_ALGOS:
            small_n = 8 if name == "tower_of_hanoi" else 200
            points, truncated = visualizer.measure(name, 0, small_n, small_n // 2 or 1, budget=10)
            self.assertFalse(truncated)
            self.assertGreaterEqual(len(points), 1)

    def test_analyze_endpoint_for_stack_push_pop(self):
        from app import app

        client = app.test_client()
        resp = client.get("/analyze?algo=stack_push_pop&step=50&n_max=200")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["complexity"], "O(n)")
        self.assertEqual(len(body["points"]), 200 // 50 + 1)

    def test_analyze_endpoint_for_tower_of_hanoi(self):
        from app import app

        client = app.test_client()
        resp = client.get("/analyze?algo=tower_of_hanoi&step=2&n_max=10")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["complexity"], "O(2^n)")

    def test_algorithms_endpoint_lists_new_entries(self):
        from app import app

        client = app.test_client()
        resp = client.get("/algorithms")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        for name in self.NEW_ALGOS:
            self.assertIn(name, body)


if __name__ == "__main__":
    unittest.main()
