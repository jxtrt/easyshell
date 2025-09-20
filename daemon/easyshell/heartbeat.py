import logging as log

class Heartbeat:
    RESPONSE_EMPTY = 0
    RESPONSE_STOP = 1
    RESPONSE_SHELL_REQUEST = 2

    def __init__(self, auth, endpoint, port=7843, on_shell_request=None):
        self.auth = auth
        self.endpoint = endpoint
        self.port = port

    def tick(self):
        log.info("Sending heartbeat to %s:%s...", self.endpoint, self.port)

        # Simulate heartbeat with input()
        val = input(">> ")
        if val == "exit":
            return Heartbeat.RESPONSE_STOP
        elif val == "enter":
            return Heartbeat.RESPONSE_SHELL_REQUEST
        else:
            return Heartbeat.RESPONSE_EMPTY