import logging


class Logger:
    def info(self, msg):
        logging.basicConfig(level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S',
                            format='%(asctime)s %(levelname)-8s %(msg)s')
        logging.info(msg)

    def error(self, msg):
        logging.basicConfig(level=logging.ERROR,
                            datefmt='%Y-%m-%d %H:%M:%S',
                            format='%(asctime)s %(levelname)-8s %(msg)s')
        logging.error(msg)
