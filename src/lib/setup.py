import os

from consts import PROCESSED_FILES_PATH, DOWNLOADED_FILES_PATH


def create_dirs():
    dirs = (PROCESSED_FILES_PATH, DOWNLOADED_FILES_PATH)
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


if __name__ == '__main__':
    create_dirs()

    from databases import create_db, data_for_databases

    create_db()
    data_for_databases()
