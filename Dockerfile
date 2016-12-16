FROM python:3.5-alpine
ENV PYTHONUNBUFFERED 1

RUN apk --update add --no-cache \
    git gcc build-base zlib-dev jpeg-dev

COPY . /app
WORKDIR /app
VOLUME /app/data

RUN pip --no-cache-dir install -r requirements.txt && \
    pip --no-cache-dir install -r /app/requirements.dev.txt

RUN make compile_messages
USER nobody
EXPOSE 8000
CMD gunicorn --workers 3 --bind 0.0.0.0:8000 manager:app --chdir=/app/opac --log-level INFO
