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
        load_dotenv()
        Config.init()

        Logger.config()
        heartbeat = Heartbeat(
            interval=Config.HEARTBEAT_INTERVAL,
            auth=None,
            endpoint=Config.HEARTBEAT_ENDPOINT,
            port=Config.HEARTBEAT_PORT,
            on_shell_request=self.handle_shell_session,
        )

        try:
            heartbeat.start()
            while True:
                pass  # Keep the main thread alive
        except KeyboardInterrupt:
            print("Shutting down...")
            heartbeat.stop()

def main():
    app = Main()
    app.run()

if __name__ == "__main__":
    main()
