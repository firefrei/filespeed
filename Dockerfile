FROM python:3-alpine

ENV PORT_INSECURE 8000
ENV PORT 8001
ENV PORT_QUIC 8002
ENV WORKERS 5


COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install hypercorn[3]

VOLUME ["/app/certs"]

EXPOSE ${PORT}
HEALTHCHECK CMD ["/bin/sh", "-c", "curl --head --user-agent healthcheck http://127.0.0.1:${PORT} || exit 1"]
ENTRYPOINT ["hypercorn"]
CMD ["--config", "file:hypercorn.config.py", "server:app"]
