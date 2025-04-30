FROM python:3.12 AS build

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN mkdir /code
WORKDIR /code

ADD pyproject.toml /code/
ADD requirements.txt /code/

ENV VIRTUAL_ENV=/opt/venv
RUN  $HOME/.local/bin/uv venv $VIRTUAL_ENV
RUN  $HOME/.local/bin/uv pip install --no-cache-dir -r requirements.txt --prerelease=allow


FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    wget \
    libpango-1.0-0 \
    libpangoft2-1.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


ENV VIRTUAL_ENV=/opt/venv
COPY --from=build $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /code

COPY . /code/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD [ "sh", "./entrypoint.sh" ]

# Collect static en caso de despligue en Heroku
ARG ENV
RUN if [ "$ENV" = "heroku" ]; then \
    python manage.py collectstatic --no-input; \
    fi