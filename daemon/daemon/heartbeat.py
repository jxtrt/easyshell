import logging as log
import requests
import uuid

class Heartbeat:
    RESPONSE_EMPTY = 0
    RESPONSE_STOP = 1
    RESPONSE_SHELL_REQUEST = 2

    def __init__(self, auth, endpoint, port=7843):
        self.auth = auth
        self.endpoint = endpoint
        self.port = port

    def tick(self):
        log.info("Sending heartbeat to %s:%s...", self.endpoint, self.port)

        # Simulate heartbeat with input()
        # val = input(">> ")
        # if val == "exit":
        #     return Heartbeat.RESPONSE_STOP
        # elif val == "enter":
        #     return Heartbeat.RESPONSE_SHELL_REQUEST
        # else:
        #     return Heartbeat.RESPONSE_EMPTY

        #perform the call!
        try:
            response = requests.post(
                f"http://{self.endpoint}:{self.port}/heartbeat",
                json={
                    "id": str(uuid.uuid4()),
                    "auth": "no-auth",
                },
                timeout=10,
            )
            response.raise_for_status()
            log.info("Heartbeat successful: %s", response.text)
        except requests.RequestException as e:
            log.error("Heartbeat request failed: %s", e)
            return Heartbeat.RESPONSE_EMPTY