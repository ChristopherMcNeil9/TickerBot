import logging


def get_logger():
    logging.basicConfig(
        filename='tickerbot.log',
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logger = logging.getLogger('tickerbot')

    return logger
