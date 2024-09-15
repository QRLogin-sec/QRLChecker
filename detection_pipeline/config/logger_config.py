import logging
import os
import urllib.parse

class LoggerConfig:
    def __init__(self, url):
        self.url = url
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.DEBUG)
        self.logger.propagate = False

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        os.makedirs("./logs", exist_ok=True)
        fh = logging.FileHandler(f"./logs/log_{urllib.parse.quote(url, safe='')}.log", mode='w')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)


    def get_logger(self):
        return self.logger
