from contextlib import contextmanager
from time import perf_counter

@contextmanager
def timed_ms():
    start = perf_counter()
    class T:
        ms: int = 0
    t = T()
    try:
        yield t
    finally:
        t.ms = int((perf_counter() - start) * 1000)
