import os
import platform

if platform.system() == 'Windows':
    HOST = 'localhost'
elif os.environ.get('DOCKER'):
    HOST = 'host.docker.internal'
else:
    HOST = '0'

PORT = 9306

NEW_FILES_PATH = '../../files'
PROCESSED_FILES_PATH = '../../processed'
