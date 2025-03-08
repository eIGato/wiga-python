__all__ = ["LockableDeque"]

import asyncio
from collections import deque
from functools import wraps


def assert_locked(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert self.lock.locked()
        return func(self, *args, **kwargs)

    return wrapper


def assert_both_locked(func):
    @wraps(func)
    def wrapper(self, other):
        assert self.lock.locked()
        if isinstance(other, LockableDeque):
            assert other.lock.locked()
        return func(self, other)

    return wrapper


class LockableDeque(deque):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = asyncio.Lock()

    append = assert_locked(deque.append)
    appendleft = assert_locked(deque.appendleft)
    clear = assert_locked(deque.clear)
    copy = assert_locked(deque.copy)
    count = assert_locked(deque.count)
    index = assert_locked(deque.index)
    insert = assert_locked(deque.insert)
    pop = assert_locked(deque.pop)
    popleft = assert_locked(deque.popleft)
    remove = assert_locked(deque.remove)
    reverse = assert_locked(deque.reverse)
    rotate = assert_locked(deque.rotate)
    __contains__ = assert_locked(deque.__contains__)
    __copy__ = assert_locked(deque.__copy__)
    __delitem__ = assert_locked(deque.__delitem__)
    __getitem__ = assert_locked(deque.__getitem__)
    __iter__ = assert_locked(deque.__iter__)
    __len__ = assert_locked(deque.__len__)
    __reduce__ = assert_locked(deque.__reduce__)
    __reversed__ = assert_locked(deque.__reversed__)
    __setitem__ = assert_locked(deque.__setitem__)
    __sizeof__ = assert_locked(deque.__sizeof__)
    extend = assert_both_locked(deque.extend)
    extendleft = assert_both_locked(deque.extendleft)
    __add__ = assert_both_locked(deque.__add__)
    __eq__ = assert_both_locked(deque.__eq__)
    __ge__ = assert_both_locked(deque.__ge__)
    __gt__ = assert_both_locked(deque.__gt__)
    __iadd__ = assert_both_locked(deque.__iadd__)
    __imul__ = assert_both_locked(deque.__imul__)
    __le__ = assert_both_locked(deque.__le__)
    __lt__ = assert_both_locked(deque.__lt__)
    __mul__ = assert_both_locked(deque.__mul__)
    __ne__ = assert_both_locked(deque.__ne__)

    def __repr__(self):
        if self.lock.locked():
            return super().__repr__()
        return "An unlocked LockableDeque"
