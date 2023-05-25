import os
import time
import asyncio
from math import ceil
from quart import Quart, request, render_template, make_response
from async_timeout import timeout

from settings import Settings

app = Quart(__name__)
app.config['MAX_CONTENT_LENGTH'] = Settings.max_content_length

def calc_timeout(payload_size:int, user_timeout:int=None) -> int:
    """
    determine timeout limit: 
    - min: Settings.timeout_min (e.g. 60s)
    - max: Settings.timeout_max (e.g. 3600s)
    - normal: 6 minutes per gigabyte or user defined
    """
    timeout = user_timeout if user_timeout else max(ceil(payload_size/(10**9) * 6 * 60), Settings.timeout_min)
    return int(min(timeout, Settings.timeout_max))

async def collect_conn_info(request):
    if request.server[1] == Settings.port_http:
        http_server = 'http'
    elif request.server[1] == Settings.port_https:
        http_server = 'https'
    elif request.server[1] == Settings.port_https_quic:
        http_server = 'quic'
    else:
        http_server = None

    return {
        'http_version': request.http_version,
        'http_scheme': request.scheme,
        'http_method': request.method,
        'http_server': http_server,
        'host': request.host.split(':')[0]
    }

@app.route('/')
async def index():
    return await render_template('index.html', 
        conn_info=await collect_conn_info(request),
        settings=Settings.__dict__
        )

@app.route('/', methods=['POST'])
async def index_post():
    upload = await upload_file()
    return await render_template('index.html', 
        upload=upload,
        conn_info=await collect_conn_info(request),
        settings=Settings.__dict__
        )


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

    # Set server-side timeout for request
    user_timeout = args.get("timeout", default=None, type=int)
    response.timeout = calc_timeout(content_bytes, user_timeout)

    # Finally, add filespeed info headers
    response.headers.update({
        "filespeed-generator": generator,
        "filespeed-chunk-size": chunk_bytes,
        "filespeed-timeout": response.timeout
    })

    return response

@app.route('/file/upload', methods=['POST'])
async def upload_file():
    user_timeout = request.args.get("timeout", default=None, type=int)
    timeout_val = calc_timeout(request.content_length, user_timeout)

    measured_rates = []
    total_payload_size = 0
    payload_size = 0
    total_time_start = time.time()
    time_start = total_time_start
    try:
        status_code = 200

        async with timeout(timeout_val):
            async for data in request.body:
                size = len(data)
                payload_size += size
                total_payload_size += size

                # Calculate upload rate
                time_now = time.time()
                time_delta = time_now-time_start
                if time_delta >= 1.0:
                    measured_rates.append(float(payload_size/time_delta))
                    time_start = time_now
                    payload_size = 0
            
    except asyncio.TimeoutError:
        status_code = 408   # 408 = request timeout

    # Calculate upload rate
    if payload_size > 0:
        time_delta = time.time()-time_start
        measured_rates.append(float(payload_size/time_delta))

    total_time_end = time.time()

    # Create Response
    data = {
        "payload_size": total_payload_size,
        "time_total": total_time_end - total_time_start,
        "upload_rate_avg": round((sum(measured_rates) / len(measured_rates)) * 8 / 1000000, 2)
    }
    headers = {
        "filespeed-timeout": timeout_val,
        "filespeed-max-content-length": request.max_content_length
    }

    return data, status_code, headers
