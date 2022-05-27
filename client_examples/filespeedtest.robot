*** Settings ***
Documentation    Test suite for evaluating download and upload performance using curl and filespeed.
...              This can be used to check the capacity of a connection.
...              Requires: 
...                - `curl` in a version that supports json output formatting with "-w" parameter
...                - `dd` for upload case
...              
...              Call example: `robot --variable HOST:filespeed filespeedtest.robot`
Metadata    Version        1.1
Metadata    Server Info    For more information about *filespeed* check https://github.com/firefrei/filespeed
Metadata    Remote Server  ${HOST}
Metadata    File Size      ${SIZE}mb

Library    Collections
Library    Process


*** Variables ***
# Connection settings
${SIZE}       100               # unit: mb
${GENERATOR}  random
${PROTOCOL}   http
${HOST}       filespeed
${URL_DL}     ${PROTOCOL}://${HOST}/file/${GENERATOR}/${SIZE}/mb
${URL_UL}     ${PROTOCOL}://${HOST}/file/upload
${CONNECT_TIMEOUT}    10

# Evaluation settings
${TEST_DL_RATE}        0.0      # unit: mbps
${TEST_DL_DURATION}    600      # unit: sec, used as download timeout
${TEST_UL_RATE}        0.0      # unit: mbps
${TEST_UL_DURATION}    600      # unit: sec, used as upload timeout


*** Test Case ***
Case Download
    [Tags]    download
    Run Download
    Log Download Metrics
    Evaluate Download Metrics

Case Upload
    [Tags]    upload
    Run Upload
    Log Upload Metrics
    Evaluate Upload Metrics


*** Keywords ***
#
# Download
#
Evaluate Download Metrics
    Should Be True    ${DOWNLOAD_METRICS.http_code} == 200    Verifying HTTP status/error code: ${DOWNLOAD_METRICS.http_code} != 200
    Should Be True    ${DOWNLOAD_METRICS.size_download} == (${SIZE}*1000000)    Verifying correct number of loaded bytes
    # Should Be True    ${DOWNLOAD_METRICS.time_connect} < 1.0    Verifying maximum connection setup time    # indicator for RTT
    # Should Be True    ${DOWNLOAD_METRICS.time_total} < 60.0    Verifying maximum download time
    # ... see end of file or curl manpage for possible parameters
    IF    ${TEST_DL_RATE} > 0.0
        Should Be True    (${DOWNLOAD_METRICS.speed_download}*8/1000000) >= ${TEST_DL_RATE}    Verifying minimum download speed above ${TEST_DL_RATE} mbps   # 1 mbps = 125000 bytes/sec
    END

Log Download Metrics
    Log Many    &{DOWNLOAD_METRICS}
    Log To Console     Download Metrics:
    FOR    ${key}    ${value}    IN    &{DOWNLOAD_METRICS}
        Log To Console    - ${key}: ${value}
    END

Run Download
    Log To Console     Running Download...
    ${download}     Run Process    curl -v -w '\%{json}' --connect-timeout ${CONNECT_TIMEOUT} --max-time ${TEST_DL_DURATION} --output /dev/null "${URL_DL}"    shell=True
    Log    ${download.stdout}
    Log    ${download.stderr}
    Should Be Equal As Integers    ${download.rc}    0    Verifying curl return code
    &{res} =    evaluate    json.loads('''${download.stdout}''')    json
    Set Suite Variable    &DOWNLOAD_METRICS    &{res}
    [Return]    &{res}

#
# Upload
#
Evaluate Upload Metrics
    Should Be True    ${UPLOAD_METRICS.http_code} == 200    Verifying HTTP status/error code: ${UPLOAD_METRICS.http_code} != 200
    Should Be True    ${UPLOAD_METRICS.size_upload} == (${SIZE}*1000000)    Verifying correct number of loaded bytes
    # Should Be True    ${UPLOAD_METRICS.time_connect} < 1.0    Verifying maximum connection setup time    # indicator for RTT
    # Should Be True    ${UPLOAD_METRICS.time_total} < 60.0    Verifying maximum upload time
    # ... see end of file or curl manpage for possible parameters
    IF    ${TEST_UL_RATE} > 0.0
        Should Be True    (${UPLOAD_METRICS.speed_upload}*8/1000000) >= ${TEST_UL_RATE}    Verifying minimum upload speed above ${TEST_UL_RATE} mbps   # 1 mbps = 125000 bytes/sec
    END

Log Upload Metrics
    Log Many    &{UPLOAD_METRICS}
    Log To Console     Upload Metrics:
    FOR    ${key}    ${value}    IN    &{UPLOAD_METRICS}
        Log To Console    - ${key}: ${value}
    END

Run Upload
    Log To Console     Running Upload...
    ${upload}     Run Process     dd if\=/dev/urandom bs\=1000 count\=${${SIZE} * 1000} | curl -v -w '\%{json}' --connect-timeout ${CONNECT_TIMEOUT} --max-time ${TEST_UL_DURATION} --output /dev/null --data-binary @- "${URL_UL}"    shell=True
    Log    ${upload.stdout}
    Log    ${upload.stderr}
    Should Be Equal As Integers    ${upload.rc}    0    Verifying curl return code
    &{res} =    evaluate    json.loads('''${upload.stdout}''')    json
    Set Suite Variable    &UPLOAD_METRICS    &{res}
    [Return]    &{res}


*** Comments ***
Possible result curl variables are (from curl manpage `man curl`):

content_type   The Content-Type of the requested document, if there was any.
errormsg       The error message. (Added in 7.75.0)
exitcode       The numerical exitcode of the transfer. (Added in 7.75.0)
filename_effective
                The ultimate filename that curl writes out to. This is only meaningful if curl is told to write to a file with the -O, --remote-name or
                -o, --output option. It's most useful in combination with the -J, --remote-header-name option. (Added in 7.26.0)
http_code      The numerical response code that was found in the last retrieved HTTP(S) or FTP(s) transfer. In 7.18.2 the alias response_code was
                added to show the same info.
http_connect   The numerical code that was found in the last response (from a proxy) to a curl CONNECT request. (Added in 7.12.4)
http_version   The http version that was effectively used. (Added in 7.50.0)
local_ip       The IP address of the local end of the most recently done connection - can be either IPv4 or IPv6. (Added in 7.29.0)
local_port     The local port number of the most recently done connection. (Added in 7.29.0)
method         The http method used in the most recent HTTP request. (Added in 7.72.0)
num_connects   Number of new connects made in the recent transfer. (Added in 7.12.3)
num_headers    The number of response headers in the most recent request (restarted at each
                redirect). Note that the status line IS NOT a header. (Added in 7.73.0)
num_redirects  Number of redirects that were followed in the request. (Added in 7.12.3)
proxy_ssl_verify_result
                The result of the HTTPS proxy's SSL peer certificate verification that was requested. 0 means the verification was successful. (Added
                in 7.52.0)
redirect_url   When an HTTP request was made without -L, --location to follow redirects (or when --max-redirs is met), this variable will show the
                actual URL a redirect would have gone to. (Added in 7.18.2)
referer        The Referer: header, if there was any. (Added in 7.76.0)
remote_ip      The remote IP address of the most recently done connection - can be either IPv4 or IPv6. (Added in 7.29.0)
remote_port    The remote port number of the most recently done connection. (Added in 7.29.0)
response_code  The numerical response code that was found in the last transfer (formerly known as "http_code"). (Added in 7.18.2)
scheme         The URL scheme (sometimes called protocol) that was effectively used. (Added in 7.52.0)
size_download  The total amount of bytes that were downloaded. This is the size of the body/data that was transfered, excluding headers.
size_header    The total amount of bytes of the downloaded headers.
size_request   The total amount of bytes that were sent in the HTTP request.
size_upload    The total amount of bytes that were uploaded. This is the size of the body/data that was transfered, excluding headers.
speed_download The average download speed that curl measured for the complete download. Bytes per second.
speed_upload   The average upload speed that curl measured for the complete upload. Bytes per second.
ssl_verify_result
                The result of the SSL peer certificate verification that was requested. 0 means the verification was successful. (Added in 7.19.0)
time_appconnect
                The time, in seconds, it took from the start until the SSL/SSH/etc connect/handshake to the remote host was completed. (Added in
                7.19.0)
time_connect   The time, in seconds, it took from the start until the TCP connect to the remote host (or proxy) was completed.
time_namelookup
                The time, in seconds, it took from the start until the name resolving was completed.
time_pretransfer
                The time, in seconds, it took from the start until the file transfer was just about to begin. This includes all pre-transfer commands
                and negotiations that are specific to the particular protocol(s) involved.
time_redirect  The time, in seconds, it took for all redirection steps including name lookup, connect, pretransfer and transfer before the final
                transaction was started. time_redirect shows the complete execution time for multiple redirections. (Added in 7.12.3)
time_starttransfer
                The time, in seconds, it took from the start until the first byte was just about to be transferred. This includes time_pretransfer and
                also the time the server needed to calculate the result.
time_total     The total time, in seconds, that the full operation lasted.
url            The URL that was fetched. (Added in 7.75.0)
urlnum         The URL index number of this transfer, 0-indexed. De-globbed URLs share the same index number as the origin globbed URL. (Added in
                7.75.0)
url_effective  The URL that was fetched last. This is most meaningful if you've told curl to follow location: headers.