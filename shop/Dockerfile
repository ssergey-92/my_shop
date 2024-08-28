FROM python:3.12

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y python3-dev \
    supervisor \
    nginx \
    netcat-openbsd\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

WORKDIR /shop/

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini
COPY ./ .
RUN chmod +x ./entrypoint.sh
RUN pip install ./frontend/dist/diploma_frontend-0.6.tar.gz

ENV PYTHONPATH="/shop:${PYTHONPATH}"

ENTRYPOINT ["/shop/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]