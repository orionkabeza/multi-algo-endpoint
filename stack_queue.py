from collections import deque


class StackEmptyError(IndexError):
    pass


class QueueEmptyError(IndexError):
    pass


class Stack:
    """LIFO stack backed by a list (append/pop from the end, both O(1))."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise StackEmptyError("pop from an empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise StackEmptyError("peek at an empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)

    def __iter__(self):
        return reversed(self._items)          # top -> bottom

    def __repr__(self):
        return f"Stack({self._items!r})"


class Queue:
    """FIFO queue backed by a deque (append/popleft, both O(1))."""

    def __init__(self):
        self._items = deque()

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if not self._items:
            raise QueueEmptyError("dequeue from an empty queue")
        return self._items.popleft()

    def peek(self):
        if not self._items:
            raise QueueEmptyError("peek at an empty queue")
        return self._items[0]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)

    def __iter__(self):
        return iter(self._items)              # front -> back

    def __repr__(self):
        return f"Queue({list(self._items)!r})"


class NaiveQueue:
    """FIFO queue backed by a plain list; dequeue() is O(n) via pop(0)."""

    def __init__(self):
        self._items = []

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if not self._items:
            raise QueueEmptyError("dequeue from an empty queue")
        return self._items.pop(0)

    def peek(self):
        if not self._items:
            raise QueueEmptyError("peek at an empty queue")
        return self._items[0]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)

    def __iter__(self):
        return iter(self._items)              # front -> back

    def __repr__(self):
        return f"NaiveQueue({self._items!r})"
