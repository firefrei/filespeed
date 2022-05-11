FROM python:3-alpine

ENV PORT 5000
ENV WORKERS 5


COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install hypercorn

EXPOSE ${PORT}
HEALTHCHECK CMD ["/bin/sh", "-c", "curl --head --user-agent healthcheck http://127.0.0.1:${PORT} || exit 1"]
CMD ["/bin/sh", "-c", "hypercorn --bind 0.0.0.0:${PORT} --workers ${WORKERS} server:app"]