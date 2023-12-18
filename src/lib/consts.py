import os
import platform

if platform.system() == 'Windows':
    HOST = 'localhost'
elif os.environ.get('DOCKER'):
    HOST = 'host.docker.internal'
else:
    HOST = '0'

PORT = 9306


def _get_path(path: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


PROCESSED_FILES_PATH = _get_path('../../processed')
DOWNLOADED_FILES_PATH = _get_path('../../downloaded')

WEB_PATH = _get_path('../web')
TEMPLATES_PATH = os.path.join(WEB_PATH, 'templates')
