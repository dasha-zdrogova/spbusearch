import os
import time
from typing import Callable

from consts import DOWNLOADED_FILES_PATH, PROCESSED_FILES_PATH, PROPERTIES_PATH


def create_dirs():
    dirs = (PROCESSED_FILES_PATH, DOWNLOADED_FILES_PATH, PROPERTIES_PATH)
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def retry(func: Callable, n=5, timeout=5.0):
    for i in range(n):
        print(f'\tattempt #{i}')
        try:
            return func()
        except Exception as e:
            print(e)
            time.sleep(timeout)
    print('could not create tables')


if __name__ == '__main__':
    from databases import create_db, data_for_databases

    print('trying to create tables')
    retry(create_db)
    print('trying to insert data into manticore')
    data_for_databases()
