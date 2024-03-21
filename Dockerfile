FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN mkdir /code
WORKDIR /code
ADD pyproject.toml /code/
ADD requirements.txt /code/
RUN python -m pip install -r requirements.txt
COPY . /code/
