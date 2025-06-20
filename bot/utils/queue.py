class MusicQueue:
    def __init__(self):
        self.queue = []

    def add(self, item):
        self.queue.append(item)

    def get_next(self):
        return self.queue.pop(0) if self.queue else None

    def clear(self):
        self.queue.clear()

    def is_empty(self):
        return len(self.queue) == 0

    def view(self):
        return self.queue.copy()
