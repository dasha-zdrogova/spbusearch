from typing import Callable
import time

import os

from consts import PROCESSED_FILES_PATH, DOWNLOADED_FILES_PATH


def create_dirs():
    dirs = (PROCESSED_FILES_PATH, DOWNLOADED_FILES_PATH)
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def retry(func: Callable, n=5, timeout=5.0):
    for _ in range(n):
        try:
            return func()
        except Exception:
            time.sleep(timeout)


if __name__ == '__main__':
    create_dirs()

    from databases import create_db, data_for_databases

    retry(create_db)
    data_for_databases()
