import logging as log
import time
from threading import Thread, Event

class Heartbeat:
    def __init__(self, interval, auth, endpoint, port=7843, on_shell_request=None):
        self.interval = interval
        self.auth = auth
        self.endpoint = endpoint
        self.port = port
        self.on_shell_request = on_shell_request

        self.running = Event()
        self.thread = None

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.running.set()
            self.thread = Thread(target=self.run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running.clear()
        if self.thread:
            self.thread.join()

    def run(self):
        log.info("Heartbeat started with interval: %s seconds", self.interval)

        while self.running.is_set():
            self._heartbeat()
            time.sleep(self.interval)

        log.info("Heartbeat stopped due to external request.")

    def _heartbeat(self):
        log.info("Sending heartbeat to %s:%s...", self.endpoint, self.port)

        # Simulate heartbeat with input()
        val = input(">> ")
        if val == "exit":
            self.running.clear()
        elif val == "enter":
            log.info("Shell request found. Passing flow back...")
            if self.on_shell_request:
                self.on_shell_request()
        else:
            log.info("No shell request found.")