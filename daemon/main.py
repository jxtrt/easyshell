import time
import logging as log
import asyncio
from dotenv import load_dotenv

from daemon.logging import Logger
from daemon.heartbeat import Heartbeat
from daemon.config import Config
from daemon.shell import Shell
from daemon.remote_shell import RemoteShell
from daemon.auth import Auth

class Main:
    def __init__(self):
        shell = Shell(Config.FORCED_SHELL)
        self.auth = Auth()
        self.remote_shell = RemoteShell(shell)

    def handle_shell_session(self, websocket_url: str, auth_type: str, auth_value: str):
        if not self.auth.validate(auth_type, auth_value):
            log.error("Authentication failed. Cannot enter remote shell session.")
            return

        log.info("Authentication passed. Accepting remote shell session.")
        asyncio.run(self.remote_shell.enter(websocket_url))

    def run(self):
        heartbeat = Heartbeat(
            instance_id=Config.INSTANCE_ID,
            auth=self.auth,
            endpoint=Config.HEARTBEAT_ENDPOINT,
            port=Config.HEARTBEAT_PORT,
        )

        running = True

        try:
            while running:
                response, response_body = heartbeat.tick()

                match response:
                    case Heartbeat.RESPONSE_SHELL_REQUEST:
                        websocket_url = response_body.get("ws_url")
                        self.handle_shell_session(websocket_url, "", "")
                    case Heartbeat.RESPONSE_EMPTY:
                        pass
                    case Heartbeat.RESPONSE_STOP:
                        running = False
                        log.info("Received stop signal. Exiting.")

                time.sleep(Config.HEARTBEAT_INTERVAL)

        except KeyboardInterrupt:
            log.info("Shutting down.")

def main():
    load_dotenv()
    Logger.config()
    Config.init()

    app = Main()
    app.run()

if __name__ == "__main__":
    main()
