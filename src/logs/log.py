import logging
from logging import Logger
from pathlib import Path

logs_dir = Path('.')


def get_log(__name__) -> Logger:
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')
    log_stream = logging.FileHandler(logs_dir / f'{__name__}.log')
    log_stream.setFormatter(formatter)
    log = logging.getLogger(__name__)
    log.addHandler(log_stream)
    log.setLevel(logging.INFO)
    return log
