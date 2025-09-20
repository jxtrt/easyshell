import time
import logging as log

from dotenv import load_dotenv

from easyshell import Logger
from easyshell import Heartbeat, Config
from easyshell.shell import Shell

class Main:
    def __init__(self):
        self.shell = Shell()        
        
    def handle_shell_session(self):
        print("Starting shell session. Type 'exit' to end.")

        while True:
            command = input("$ ")
            if command.strip().lower() == "exit":
                print("Exiting shell session.")
                break

            result = self.shell.run_line(command)
            print(result["stdout"], end="")
            if result["stderr"]:
                print(result["stderr"], end="")

    def run(self):
        heartbeat = Heartbeat(
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
