import os
from math import ceil
from quart import Quart, request, render_template

app = Quart(__name__)


@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/file/<generator>/<int:sz>')
@app.route('/file/<generator>/<int:sz>/<unit>')
async def generate_file(sz, unit="mb", generator="random"):
    args = request.args

    unit = unit.lower()
    if unit == "b":
        scale = 1
    elif unit == "kb":
        scale = 10**3
    elif unit == "gb":
        scale = 10**9
    elif unit == "tb":
        scale = 10**12
    else:
        scale = 10**6

    content_bytes = sz * scale
    chunk_bytes = args.get("chunk_size", default=1000, type=int)
    chunk_num = ceil(content_bytes/chunk_bytes)

    async def generate_urandom():
        bytes_remaining = content_bytes
        while bytes_remaining > 0:
            for _ in range(0, chunk_num):
                size = chunk_bytes if bytes_remaining > chunk_bytes else bytes_remaining
                bytes_remaining = bytes_remaining - size
                yield os.urandom(size)
    
    async def generate_zero():
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
        mimetype = "application/octet-stream",
        headers = {
            "Content-Length": content_bytes,
            "Content-Disposition": "attachment; filename=%d.bin" % (content_bytes)
        })

