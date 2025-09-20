import time
import logging as log

from dotenv import load_dotenv

from daemon import Logger
from daemon import Heartbeat, Config
from daemon.shell import Shell

class Main:
    def __init__(self):
        self.shell = Shell(Config.FORCED_SHELL)        
        
    def handle_shell_session(self):
        print("Starting shell session. Type 'exit' to end.")
        self.shell.enter()

    def run(self):
        heartbeat = Heartbeat(
            instance_id=Config.INSTANCE_ID,
            auth=None,
            endpoint=Config.HEARTBEAT_ENDPOINT,
            port=Config.HEARTBEAT_PORT,
        )

        running = True

        try:
            while running:
                response = heartbeat.tick()

                match response:
                    case Heartbeat.RESPONSE_SHELL_REQUEST:
                        self.handle_shell_session()
                    case Heartbeat.RESPONSE_EMPTY:
                        pass
                    case Heartbeat.RESPONSE_STOP:
                        running = False
                        log.info("Received stop signal. Exiting...")

                time.sleep(Config.HEARTBEAT_INTERVAL)

        except KeyboardInterrupt:
            print("Shutting down...")

def main():
    load_dotenv()
    Logger.config()
    Config.init()

    app = Main()
    app.run()

if __name__ == "__main__":
    main()
