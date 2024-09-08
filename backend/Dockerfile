FROM python:3.12.2-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml poetry.lock BACKEND.md ./

RUN pip3 install --upgrade pip
RUN pip3 install poetry
RUN poetry check

RUN /bin/true\
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction \
    && rm -rf /root/.cache/pypoetry

