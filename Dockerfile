FROM python:3.11

WORKDIR /code

ENV DOCKER=true

# VOLUME ./manticore/data /var/lib/manticore

# RUN apt-get -yqq update && apt-get -yqq install docker.io

# VOLUME /var/run/docker.sock

# RUN dockerd

# RUN docker run -e EXTRA=1 --name manticore -p 9306:9306 -d manticoresearch/manticore

RUN pip3 install poetry

COPY ./poetry.lock ./pyproject.toml /code/

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --only main --no-interaction --no-root

COPY ./src /code/src

# RUN python /code/src/lib/setup.py

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
