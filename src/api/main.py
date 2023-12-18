from dataclasses import asdict

from fastapi import FastAPI

from ..lib import databases

app = FastAPI()


@app.get('/search')
async def get(search_str: str):
    return [asdict(match) for match in databases.get_matches(search_str)]


@app.get('/hello')
async def hello():
    return 'hello'
