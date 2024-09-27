FROM python:3.12

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y python3-dev \
    supervisor \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip poetry==1.8.3

WORKDIR /bank/

COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini
COPY ./poetry.lock .
COPY ./pyproject.toml .

RUN poetry config virtualenvs.create false --local && poetry install

COPY ./ .

#ENV PYTHONPATH="/bank:${PYTHONPATH}"

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]