FROM python:3.12

WORKDIR /code

ENV DOCKER=true

RUN pip3 install poetry

COPY ./pyproject.toml .

RUN POETRY_VIRTUALENVS_CREATE=false poetry lock
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --only main --no-interaction --no-root

COPY ./src ./src
COPY ./downloaded ./downloaded
COPY ./properties ./properties

ENTRYPOINT python3 ./src/lib/setup.py && uvicorn src.api.main:app --host 0.0.0.0 --port 5000
