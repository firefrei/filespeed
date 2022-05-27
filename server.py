import os
import time
from math import ceil
from quart import Quart, request, render_template, make_response
from async_timeout import timeout


app = Quart(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10**10

def calc_timeout(payload_size) -> int:
    """
    determine timeout limit: 
    - min: 60s
    - max: 3600s
    - normal: 6 minutes per gigabyte or user defined
    """
    timeout = max(ceil(payload_size/(10**9) * 6 * 60), 60)
    return int(min(timeout, 3600))

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/file/<generator>/<int:sz>')
@app.route('/file/<generator>/<int:sz>/<unit>')
async def download_file(sz, unit="mb", generator="random"):
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

    # Define and choose generator
    async def generate_random():
        bytes_remaining = content_bytes
        while bytes_remaining > 0:
            size = min(chunk_bytes, bytes_remaining)
            bytes_remaining = bytes_remaining - size
            yield os.urandom(size)

    async def generate_zero():
        zeroes = bytes(chunk_bytes)
        bytes_remaining = content_bytes
        while bytes_remaining > 0:
            size = min(chunk_bytes, bytes_remaining)
            bytes_remaining = bytes_remaining - size
            yield zeroes if size == chunk_bytes else bytes(size)

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
        default = calc_timeout(content_bytes),
        type = int)
    response.timeout = int(min(response.timeout, 3600))
    
    # Finally, add filespeed info headers
    response.headers.update({
        "filespeed-generator": generator,
        "filespeed-chunk-size": chunk_bytes,
        "filespeed-timeout": response.timeout
    })

    return response

@app.route('/file/upload', methods=['POST'])
async def upload_file():
    timeout_val = calc_timeout(request.content_length)

    payload_size = 0
    time_start = time.time()
    async with timeout(timeout_val):
        async for data in request.body:
            payload_size += len(data)
    time_end = time.time()
    
    # Create Response
    data = {
        "payload_size": payload_size,
        "time_total": time_end - time_start
    }
    headers = {
        "filespeed-timeout": timeout_val,
        "filespeed-max-content-length": request.max_content_length
    }
    status_code = 200

    return data, status_code, headers
