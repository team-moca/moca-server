import time

from core.exceptions import TimeoutException


class Pool:
    def __init__(self):
        self.pool = {}
        self.topics = []

    def listen(self, topic: str):
        self.topics.append(topic)

    def push(self, topic, message):
        if topic in self.topics:
            self.pool[topic] = message

    def _get(self, topic):
        response = self.pool.get(topic)

        if response:
            del self.pool[topic]

        return response

    def get(self, topic, timeout=10):
        elapsed = 0
        while True:
            response = self._get(topic)
            if response:
                return response

            if elapsed > timeout:
                raise TimeoutException(f"Timeout while waiting for topic {topic}.")

            time.sleep(0.02)
            elapsed += 0.02
