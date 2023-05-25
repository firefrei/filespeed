from os import getenv


class Settings:
    port_http = int(getenv("PORT_HTTP", 8000))
    port_https = int(getenv("PORT_HTTPS", 8001))
    port_https_quic = int(getenv("PORT_HTTPS_QUIC", 8002))

    certfile = getenv("CERTFILE", "certs/server.crt")
    keyfile = getenv("KEYFILE", "certs/server.key")
    workers = int(getenv("WORKERS", 5))

    max_content_length = int(getenv("MAX_CONTENT_LENGTH", 10**10))
    timeout_min = int(getenv("TIMEOUT_MIN", 60))
    timeout_max = int(getenv("TIMEOUT_MAX", 3600))
