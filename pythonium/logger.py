import logging
import sys


class ContextLogger(logging.Logger):

    def _log(self, level, msg, args, exc_info=None, extra=None):
        msg = f"{msg} - "
        if extra:
            msg = f"{msg}{'; '.join((f'{k}={v}' for k, v in extra.items()))}"
        super()._log(level, msg, args, exc_info, extra)


def get_logger(name, lvl=logging.INFO, filename=None):

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(module)s:%(funcName)s %(message)s')

    logging.setLoggerClass(ContextLogger)
    logger = logging.getLogger(name)

    if filename:
        handler = logging.FileHandler(filename)
        handler.setFormatter(formatter)
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(lvl)

    return logger

