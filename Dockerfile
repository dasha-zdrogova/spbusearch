FROM python:3.11

WORKDIR /code

ENV DOCKER=true

RUN pip3 install poetry

COPY ./poetry.lock ./pyproject.toml /code/

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --only main --no-interaction --no-root

COPY ./src /code/src

# RUN python /code/src/lib/setup.py

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
