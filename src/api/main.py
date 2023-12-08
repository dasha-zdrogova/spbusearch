from dataclasses import asdict

from fastapi import FastAPI

from ..lib import databases

app = FastAPI()


@app.get('/search')
async def read_root(search_str: str):
    return [asdict(match.to_result(search_str)) for match in databases.get_matches(search_str)]


@app.get('/items/{item_id}')
async def read_item(item_id: int, q: str | None = None):
    return {'item_id': item_id, 'q': q}
