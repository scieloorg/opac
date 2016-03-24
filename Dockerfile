FROM python:2.7

COPY . /app

WORKDIR /app
VOLUME /app/data

# dependêcias:
RUN pip install -r requirements.txt && \
    pip install -r requirements.dev.txt && \
    pip install -r requirements.production.txt

# portas
EXPOSE 8000

CMD gunicorn --workers 3 --bind 0.0.0.0:8000 opac.manager:app --chdir=/app --log-level DEBUG
