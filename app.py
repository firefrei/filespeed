import os
from math import ceil
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/file/<generator>/<int:mb>')
@app.route('/file/<generator>/<int:mb>/<unit>')
def generate_file(mb, unit="mb", generator="random"):
    args = request.args

    scale = 10**6
    unit = unit.lower()
    if unit == "b":
        scale = 1
    elif unit == "kb":
        scale = 10**3
    elif unit == "gb":
        scale = 10**9
    elif unit == "tb":
        scale = 10**12

    content_bytes = mb * scale
    chunk_bytes = args.get("chunk_size", default=1000, type=int)
    chunk_num = ceil(content_bytes/chunk_bytes)

    def generate_urandom():
        bytes_remaining = content_bytes
        while bytes_remaining > 0:
            for _ in range(0, chunk_num):
                size = chunk_bytes if bytes_remaining > chunk_bytes else bytes_remaining
                bytes_remaining = bytes_remaining - size
                yield os.urandom(size)
    
    def generate_zero():
        bytes_remaining = content_bytes
        zeroes = bytes(chunk_bytes)
        while bytes_remaining > 0:
            for _ in range(0, chunk_num):
                size = chunk_bytes if bytes_remaining > chunk_bytes else bytes_remaining
                bytes_remaining = bytes_remaining - size
                yield zeroes
    
    generator_fun = generate_zero if generator == "zero" else generate_urandom

    return app.response_class(
        generator_fun(), 
        mimetype="application/octet-stream",
        headers={
            "Content-Length": content_bytes,
            "Content-Disposition": "attachment; filename=%d.bin" % (content_bytes)
        })

