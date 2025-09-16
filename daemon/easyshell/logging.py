import logging as log


class Logger:
    @staticmethod
    def config():
        log.basicConfig(
            level=log.INFO, format="[%(asctime)s] [%(levelname)s]: %(message)s"
        )
        log.info("Logger configured")
