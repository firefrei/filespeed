# Check if certificates exist... else create
from os.path import exists, isdir
if not exists("certs/server.key") or not exists("certs/server.crt"):
    print("Certificate files do not exist. Going to create self-signed certificates...")
    if not isdir("certs"):
        from os import mkdir
        mkdir("certs")

    import subprocess
    ret = subprocess.call(["openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", "certs/server.key", "-out", "certs/server.crt", "-sha256", "-days", "365", "-nodes", "-subj", "/C=DE/ST=Bavaria/L=Germany/O=filespeed/OU=server/CN=filespeed"])
    if ret != 0:
      raise RuntimeError("Could not create self-signed certificate")

# Hypercorn settings
from os import getenv
insecure_bind = ["0.0.0.0:%s" % (getenv("PORT_HTTP", 8000)), "[::]:%s" % (getenv("PORT_HTTP", 8000))]
bind = ["0.0.0.0:%s" % (getenv("PORT_HTTPS", 8001)), "[::]:%s" % (getenv("PORT_HTTPS", 8001))]
quic_bind = ["0.0.0.0:%s" % (getenv("PORT_HTTPS_QUIC", 8002)), "[::]:%s" % (getenv("PORT_HTTPS_QUIC", 8002))]

certfile = getenv("CERTFILE", "certs/server.crt")
keyfile = getenv("KEYFILE", "certs/server.key")
workers = int(getenv("WORKERS", 5))
