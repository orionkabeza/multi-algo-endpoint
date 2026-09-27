import math
import random

from stack_queue import NaiveQueue, Queue, Stack


def linear_setup(n):
    return list(range(n)), -1            # target absent -> worst case


def linear_search(data):
    arr, target = data
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1


def binary_setup(n):
    return list(range(n)), -1


def binary_search(data):
    arr, target = data
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def reversed_setup(n):
    return list(range(n, 0, -1))         # worst case for bubble/insertion


def bubble_sort(data):
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def size_setup(n):
    return n


def nested_loops(n):
    count = 0
    for _ in range(n):
        for _ in range(n):
            count += 1
    return count

def nested_loops1(n):
    users = [{'id': i} for i in range(n)]
    
    for i in range(len(users)):
        seen = False
        for j in range(len(users)):
            if users[i]['id'] == users[j]['id']:
                seen = True
                break
        if not seen:
            n.append(n[i])

# ---- bonus algorithms (+2 points each) ----

def selection_sort(data):
    arr = data[:]
    n = len(arr)
    for i in range(n):
        smallest = i
        for j in range(i + 1, n):
            if arr[j] < arr[smallest]:
                smallest = j
        arr[i], arr[smallest] = arr[smallest], arr[i]
    return arr


def insertion_sort(data):
    arr = data[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def random_setup(n):
    rng = random.Random(42)              # fixed seed -> repeatable
    return [rng.random() for _ in range(n)]


def merge_sort(data):
    if len(data) <= 1:
        return data[:]
    mid = len(data) // 2
    left, right = merge_sort(data[:mid]), merge_sort(data[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(data):
    if len(data) <= 1:
        return data[:]
    pivot = data[len(data) // 2]
    return (quick_sort([x for x in data if x < pivot])
            + [x for x in data if x == pivot]
            + quick_sort([x for x in data if x > pivot]))


def constant_time(data):
    return data[0] if data else None


def jump_setup(n):
    return list(range(n)), n             # target larger than every item -> worst case


def jump_search(data):
    arr, target = data
    n = len(arr)
    if n == 0:
        return -1
    block = int(math.sqrt(n))
    prev = 0
    while prev < n and arr[min(prev + block, n) - 1] < target:
        prev += block                    # jump ahead one block at a time
    for i in range(prev, min(prev + block, n)):
        if arr[i] == target:
            return i
    return -1


def fibonacci_recursive(n):
    if n < 2:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def permutations(n):
    count = 0

    def walk(remaining):
        nonlocal count
        if not remaining:
            count += 1
            return
        for i in range(len(remaining)):
            walk(remaining[:i] + remaining[i + 1:])

    walk(list(range(n)))
    return count


def matrix_setup(n):
    rng = random.Random(42)
    a = [[rng.random() for _ in range(n)] for _ in range(n)]
    b = [[rng.random() for _ in range(n)] for _ in range(n)]
    return a, b


def matrix_multiplication(data):
    a, b = data
    n = len(a)
    result = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0.0
            for k in range(n):
                total += a[i][k] * b[k][j]
            result[i][j] = total
    return result


def heap_sort(data):
    arr = data[:]
    n = len(arr)

    def sift_down(root, end):
        while True:
            child = 2 * root + 1
            if child >= end:
                return
            if child + 1 < end and arr[child] < arr[child + 1]:
                child += 1
            if arr[root] >= arr[child]:
                return
            arr[root], arr[child] = arr[child], arr[root]
            root = child

    for start in range(n // 2 - 1, -1, -1):
        sift_down(start, n)
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        sift_down(0, end)
    return arr


# ---- stack & queue algorithms ----

def stack_setup(n):
    return list(range(n))


def stack_push_pop(data):
    s = Stack()
    for item in data:
        s.push(item)
    result = []
    while not s.is_empty():
        result.append(s.pop())
    return result


def queue_setup(n):
    return list(range(n))


def queue_enqueue_dequeue(data):
    q = Queue()
    for item in data:
        q.enqueue(item)
    result = []
    while not q.is_empty():
        result.append(q.dequeue())
    return result


def naive_queue_enqueue_dequeue(data):
    # pop(0) shifts every remaining element -> O(n) per dequeue, O(n^2) total.
    q = NaiveQueue()
    for item in data:
        q.enqueue(item)
    result = []
    while not q.is_empty():
        result.append(q.dequeue())
    return result


def balanced_setup(n):
    return "(" * n + ")" * n                 # fully nested -> worst case stack depth


_BRACKET_PAIRS = {")": "(", "]": "[", "}": "{"}


def balanced_parentheses(data):
    s = Stack()
    for ch in data:
        if ch in "([{":
            s.push(ch)
        elif ch in _BRACKET_PAIRS:
            if s.is_empty() or s.pop() != _BRACKET_PAIRS[ch]:
                return False
    return s.is_empty()


def next_greater_elements(data):
    # each index is pushed and popped at most once -> amortized O(n)
    result = [-1] * len(data)
    s = Stack()
    for i, value in enumerate(data):
        while not s.is_empty() and data[s.peek()] < value:
            result[s.pop()] = value
        s.push(i)
    return result


def graph_setup(n):
    graph = {i: [] for i in range(n)}
    for i in range(n - 1):                   # path graph: 0-1-2-...-(n-1)
        graph[i].append(i + 1)
        graph[i + 1].append(i)
    return graph


def bfs_traversal(graph):
    if not graph:
        return []
    start = 0
    visited = {start}
    order = []
    q = Queue()
    q.enqueue(start)
    while not q.is_empty():
        node = q.dequeue()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                q.enqueue(neighbor)
    return order


def hanoi_setup(n):
    return n


def tower_of_hanoi(n):
    source, aux, target = Stack(), Stack(), Stack()
    for disk in range(n, 0, -1):
        source.push(disk)

    moves = 0

    def move(count, src, buf, dst):
        nonlocal moves
        if count == 0:
            return
        move(count - 1, src, dst, buf)
        dst.push(src.pop())
        moves += 1
        move(count - 1, buf, src, dst)

    move(n, source, aux, target)
    return moves


# name -> (setup, run, big-O label, max_n)
# max_n keeps a single run short enough to finish. The time budget is only
# checked between points, so it cannot interrupt one huge run.
ALGORITHMS = {
    "linear_search":         (linear_setup,   linear_search,         "O(n)",       1_000_000),
    "binary_search":         (binary_setup,   binary_search,         "O(log n)",   1_000_000),
    "bubble_sort":           (reversed_setup, bubble_sort,           "O(n^2)",     10_000),
    "nested_loops":          (size_setup,     nested_loops,          "O(n^2)",     10_000),
    "selection_sort":        (random_setup,   selection_sort,        "O(n^2)",     10_000),
    "insertion_sort":        (reversed_setup, insertion_sort,        "O(n^2)",     10_000),
    "merge_sort":            (random_setup,   merge_sort,            "O(n log n)", 1_000_000),
    "quick_sort":            (random_setup,   quick_sort,            "O(n log n)", 1_000_000),
    "constant_time":         (random_setup,   constant_time,         "O(1)",       1_000_000),
    "jump_search":           (jump_setup,     jump_search,           "O(sqrt n)",  1_000_000),
    "heap_sort":             (random_setup,   heap_sort,             "O(n log n)", 1_000_000),
    "matrix_multiplication": (matrix_setup,   matrix_multiplication, "O(n^3)",     250),
    "fibonacci_recursive":   (size_setup,     fibonacci_recursive,   "O(2^n)",     35),
    "permutations":          (size_setup,     permutations,          "O(n!)",      10),

    # ---- stack & queue algorithms ----
    "stack_push_pop":              (stack_setup,    stack_push_pop,              "O(n)",     1_000_000),
    "queue_enqueue_dequeue":       (queue_setup,    queue_enqueue_dequeue,       "O(n)",     1_000_000),
    "naive_queue_enqueue_dequeue": (queue_setup,    naive_queue_enqueue_dequeue, "O(n^2)",   10_000),
    "balanced_parentheses":        (balanced_setup, balanced_parentheses,       "O(n)",     1_000_000),
    "next_greater_elements":       (random_setup,   next_greater_elements,      "O(n)",     1_000_000),
    "bfs_traversal":               (graph_setup,    bfs_traversal,              "O(n)",     1_000_000),
    "tower_of_hanoi":              (hanoi_setup,    tower_of_hanoi,             "O(2^n)",   20),
}
