FROM python:3-alpine

ENV PORT=5000


COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE ${PORT}
CMD ["/bin/sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} wsgi:app"]