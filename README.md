# Filespeed
## HTTP payload generator for client-side speed tests and connection benchmarks

The simplest speed test: Download a file!  
However, many alternative solutions generate files in-advance and serve them via a webserver. Consequently, the larger the files you want to provide, the more disk space you need to statically allocate to store them. Especially in cloud-native environments, where your speed test server can be deployed on multiple nodes, this is a challenge.  
  
Filespeed simply generates the served file content on-the-fly using generators. The goal of Filespeed is to enable performance measurements based on existing methods (file/block download) rather than inventing a new speed test client. It uses a common HTTP webserver that will serve your requests. On your client, you can use any performance-optimized tool of your choice: Your browser, curl, wget, ...  
  
Filespeed offers a index page with download links of example size. However, using the Filespeed URL format, you can easily generate and download a file with your desired characteristics. The file content can be generated with random bytes (from /dev/urandom) or using simple zeros (null byte).  


## Run using Docker
```bash
docker run --rm --name filespeed firefrei/filespeed
```

Access http://localhost:5000 in your browser!


## Client examples

Using curl:
```bash
curl --output /dev/null http://localhost:5000/file/random/10/gb

# Optional parameters:
#  --http1.1     -> force http version 1.1 (mostly default)
#  --http2       -> force http version 2 which supports multiplexing
```

Using wget:
```bash
wget -O /dev/null http://localhost:5000/file/random/10/gb

# Optional parameters:
#   --report-speed=bits     -> report measured rate in bit rather than bytes per second
```