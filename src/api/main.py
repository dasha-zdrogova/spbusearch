from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..lib import consts, databases

app = FastAPI()

templates = Jinja2Templates(directory=consts.TEMPLATES_PATH)


def get_matches_json(
    search_str: str,
    code: Optional[str] = None,
    field: Optional[str] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
):
    return [asdict(match) for match in databases.get_matches(search_str, code, field, level, name)]


@app.get('/api/search')
async def get(
    search_str: str,
    code: Optional[str] = None,
    field: Optional[str] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
):
    return get_matches_json(search_str, code, field, level, name)


@app.get('/search', response_class=HTMLResponse)
async def search(
    request: Request,
    search_str: str,
    code: Optional[str] = None,
    field: Optional[str] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
):
    return templates.TemplateResponse(
        'search_result.html',
        {'request': request, 'matchess': get_matches_json(search_str, code, field, level, name)},
    )


@app.get('/hello')
async def hello():
    return 'hello'
