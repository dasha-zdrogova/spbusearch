from dataclasses import asdict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..lib import databases, consts

app = FastAPI()

templates = Jinja2Templates(directory=consts.TEMPLATES_PATH)


def get_matches_json(search_str: str):
    return [asdict(match) for match in databases.get_matches(search_str)]


@app.get('/api/search')
async def get(search_str: str):
    return get_matches_json(search_str)


@app.get('/search', response_class=HTMLResponse)
async def search(request: Request, search_str: str):
    return templates.TemplateResponse(
        'search_result.html',
        {'request': request, 'matchess': get_matches_json(search_str)},
    )


@app.get('/hello')
async def hello():
    return 'hello'
