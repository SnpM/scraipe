import threading

class AtomicInteger:
    def __init__(self, initial=0):
        self.value = initial
        self._lock = threading.Lock()

    def get_and_increment(self):
        with self._lock:
            val = self.value
            self.value += 1
            return val

    def increment_and_get(self):
        with self._lock:
            self.value += 1
            return self.value

    def get(self):
        with self._lock:
            return self.value