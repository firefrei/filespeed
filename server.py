import os
from math import ceil
from quart import Quart, request, render_template, make_response

app = Quart(__name__)


@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/file/<generator>/<int:sz>')
@app.route('/file/<generator>/<int:sz>/<unit>')
async def generate_file(sz, unit="mb", generator="random"):
    args = request.args
    generator = generator if generator in ["random", "zero"] else "random"

    # Determine final content size
    unit = unit.lower()
    if unit == "b":
        scale = 1
    elif unit == "kb":
        scale = 10**3
    elif unit == "gb":
        scale = 10**9
    elif unit == "tb":
        scale = 10**12
    elif unit == "kib":
        scale = 2**10
    elif unit == "mib":
        scale = 2**20
    elif unit == "gib":
        scale = 2**30
    elif unit == "tib":
        scale = 2**40
    else:
        scale = 10**6

    content_bytes = sz * scale

    # Set default chunk size according to quart file read / IOBody (ResponseBody) buffer size
    # https://github.com/pgjones/quart/blob/6a40acc61735bbac770b998caa26e8144ddfdfa5/src/quart/wrappers/response.py#L179
    chunk_bytes = args.get("chunk_size", default=8192, type=int)
    chunk_num = ceil(content_bytes/chunk_bytes)

    # Define and choose generator
    async def generate_random():
        bytes_remaining = content_bytes
        while bytes_remaining > 0:
            for _ in range(0, chunk_num):
                size = chunk_bytes if bytes_remaining > chunk_bytes else bytes_remaining
                bytes_remaining = bytes_remaining - size
                yield os.urandom(size)

    async def generate_zero():
        zeroes = bytes(chunk_bytes)
        bytes_remaining = content_bytes
        while bytes_remaining > 0:
            for _ in range(0, chunk_num):
                size = chunk_bytes if bytes_remaining > chunk_bytes else bytes_remaining
                bytes_remaining = bytes_remaining - size
                yield zeroes if size == chunk_bytes else bytes(bytes_remaining)

    generator_fun = generate_zero if generator == "zero" else generate_random
    
    # Create response object
    response = await make_response(generator_fun())
    response.headers.update({
            "Content-Type": "application/octet-stream",
            "Content-Length": content_bytes,
            "Content-Disposition": "attachment; filename=%d.bin" % (content_bytes)
        })

    # define timeout limit: 
    # - min: 60s
    # - max: 3600s
    # - normal: 6 minutes per gigabyte or user defined
    response.timeout = args.get("timeout",
        default = max(ceil(content_bytes/(10**9) * 6 * 60), 60),
        type = int)
    response.timeout = int(min(response.timeout, 3600))
    
    # Finally, add filespeed info headers
    response.headers.update({
        "filespeed-generator": generator,
        "filespeed-chunk-size": chunk_bytes,
        "filespeed-timeout": response.timeout
    })

    return response
