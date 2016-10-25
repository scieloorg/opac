FROM python:2.7
ENV PYTHONUNBUFFERED 1
COPY . /app
WORKDIR /app
VOLUME /app/data
RUN pip install -r requirements.txt && \
    pip install -r /app/requirements.dev.txt
RUN make compile_messages
USER nobody
EXPOSE 8000
CMD gunicorn --workers 3 --bind 0.0.0.0:8000 manager:app --chdir=/app/opac --log-level INFO
