from dotenv import load_dotenv

from easyshell import Logger
from easyshell import Heartbeat, Config


def main():
    load_dotenv()
    Config.init()

    Logger.config()
    heartbeat = Heartbeat(
        interval=Config.HEARTBEAT_INTERVAL,
        auth=None,
        endpoint=Config.HEARTBEAT_ENDPOINT,
        port=Config.HEARTBEAT_PORT,
    )
    heartbeat.run()
    

if __name__ == "__main__":
    main()
