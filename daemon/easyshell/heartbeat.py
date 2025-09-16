import logging as log
import time

class Heartbeat:
    def __init__(self, interval, auth, endpoint, port=7843):
        self.interval = interval
        self.auth = auth
        self.endpoint = endpoint
        self.port = port
        
        self.running = True

    def run(self):
        log.info("Heartbeat started with interval: %s seconds", self.interval)

        while self.running:
            self._heartbeat()
            time.sleep(self.interval)
        
    def _heartbeat(self):
        log.info("Sending heartbeat to %s:%s...", self.endpoint, self.port)
        

    def handle_signal(self, signum, frame):
        log.info("Received signal %s, stopping heartbeat...", signum)