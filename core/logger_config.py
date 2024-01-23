from sys import stderr
from loguru import logger


def setup_logger():
    logger.remove()
    format_string = '<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{name}</cyan>'
    format_string += ' | <white>{message}</white>'

    logger.add(
        stderr,
        format=format_string
    )
