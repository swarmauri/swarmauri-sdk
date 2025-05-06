import time


class DurationManager:
    def __enter__(self):
        # Store the start time when entering the context
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Calculate the duration when exiting the context
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
