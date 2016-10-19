FROM python:2.7
ENV PYTHONUNBUFFERED 1
USER nobody
COPY . /app
WORKDIR /app
VOLUME /app/data
RUN pip install -r requirements.txt && \
    pip install -r requirements.dev.txt && \
    pip install -r requirements.production.txt
EXPOSE 8000
CMD gunicorn --workers 3 --bind 0.0.0.0:8000 manager:app --chdir=/app/opac --log-level DEBUG
