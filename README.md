# HTTP payload generator for client-side speed tests and connection benchmarks

The simplest speed test: Download a file!  
However, many alternative solutions generate files in-advance and serve them via a webserver. Consequently, the larger the files you want to provide, the more disk space you need to statically allocate to store them. Especially in cloud-native environments, where your speed test server can be deployed on multiple nodes, this is a challenge.  

Filespeed simply generates the served file content on-the-fly using generators. It provides a HTTP webserver that will serve your requests.  



## Run using Docker
```bash
docker run --rm --name filespeed firefrei/filespeed
```

Access http://localhost:5000 in your browser!


## Client examples

Using curl:
```
curl --output /dev/null http://localhost:5000/file/random/10/gb
```

Using wget:
```
wget -O /dev/null [--report-speed=bits] http://localhost:5000/file/random/10/gb
```