FROM python:3-alpine

ENV GID 900
ENV UID 900

ENV PORT_HTTP 8000
ENV PORT_HTTPS 8001
ENV PORT_HTTPS_QUIC 8002
ENV WORKERS 5


COPY . /app
WORKDIR /app

RUN apk add --no-cache --virtual builddeps build-base bsd-compat-headers openssl-dev \
    && apk add --no-cache openssl \
    && pip install -r requirements.txt \
    && pip install hypercorn[3] aioquic \
    && apk del --purge builddeps

RUN addgroup -S -g ${GID} filespeed \
  && adduser -S -u ${UID} -G filespeed filespeed

# Set user and group using IDs instead of names. Kubernetes needs this to identify non-root users.
USER ${UID}:${GID}


VOLUME ["/app/certs"]

EXPOSE ${PORT_HTTP}/tcp ${PORT_HTTPS}/tcp ${PORT_HTTPS_QUIC}/udp
HEALTHCHECK CMD ["/bin/sh", "-c", "curl --head --user-agent healthcheck http://127.0.0.1:${PORT_HTTP} || exit 1"]
ENTRYPOINT ["hypercorn"]
CMD ["--config", "file:hypercorn.config.py", "server:app"]
