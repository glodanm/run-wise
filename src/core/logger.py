import contextvars
import logging
import sys


request_ip_var = contextvars.ContextVar("request_ip", default="-")


class LogFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(client_ip)s] - [%(message)s] [(%(filename)s:%(lineno)d)]"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        record.client_ip = request_ip_var.get()
        # return super().format(record)
        return formatter.format(record)


def setup_logging(level=logging.DEBUG) -> None:

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LogFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers = [handler]
    uvicorn_access.setLevel(level)

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = [handler]
    uvicorn_logger.setLevel(level)

    logging.getLogger("uvicorn").setLevel(logging.INFO)
