import logging
import sys


def setup_loggger(
    color: bool = True,
    name: str = "wikisearch",
    disable: bool = False,
):
    if disable:
        return None

    logger = logging.getLogger(name)
    logger.propagate = False

    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")

    plain_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    if color:
        from termcolor import colored

        formatter = ColorfulFormatter(
            colored("%(asctime)s | %(name)s: ", "green") + "%(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = plain_formatter

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    warnings_logger.addHandler(ch)
    handlers = []
    handlers.append(ch)
    logging.basicConfig(level=logging.INFO, handlers=handlers)

    return logger


# taken from mmf
class ColorfulFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def formatMessage(self, record):
        from termcolor import colored

        log = super().formatMessage(record)
        if record.levelno == logging.WARNING:
            prefix = colored("WARNING", "red", attrs=["blink"])
        elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
            prefix = colored("ERROR", "red", attrs=["blink", "underline"])
        else:
            return log
        return prefix + " " + log


logger = setup_loggger(color=True)
