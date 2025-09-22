import logging as log
import requests

class Heartbeat:
    RESPONSE_EMPTY = 0
    RESPONSE_STOP = 1
    RESPONSE_SHELL_REQUEST = 2

    def __init__(self, instance_id, auth, endpoint, port=7843):
        self.instance_id = instance_id
        self.auth = auth
        self.endpoint = endpoint
        self.port = port

    def tick(self) -> tuple[int, dict]:
        log.info("Sending heartbeat to %s:%s.", self.endpoint, self.port)

        try:
            response_code = Heartbeat.RESPONSE_EMPTY

            response = requests.post(
                f"http://{self.endpoint}:{self.port}/heartbeat",
                json={
                    "id": self.instance_id,
                    "auth_type": "otp",
                },
                timeout=10,
            )
            response.raise_for_status()

            response_json = response.json()
            status = response_json.get("status", "nop")

            match status:
                case "stop":
                    log.info("Received stop command from server.")
                    response_code = Heartbeat.RESPONSE_STOP
                case "shell_request":
                    log.info("Received shell request from server.")
                    response_code = Heartbeat.RESPONSE_SHELL_REQUEST
                case "nop":
                    log.info("No operation requested by server.")
                    response_code = Heartbeat.RESPONSE_EMPTY
                case _:
                    log.warning("Unknown status received: %s", status)

            return response_code, response_json

        except requests.RequestException as e:
            log.error("Heartbeat request failed: %s", e)
            return response_code, {}