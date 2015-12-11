docker-caching-test
===================

A testcase to review the current state of docker cache reuse.


Hypothesis
----------
Irrespectively whether we use docker build or docker-compose build or python docker_py client cache should be fully reusable.


Current state (2015-12)
-----------------------
`docker build` and `docker-compose build` will create unique layers (won't reuse cache from each other) whenever a file is added (ADD/COPY)

Imagine simple Dockerfile:
```
FROM alpine

RUN  du -s /
COPY important.txt /
RUN  du -s /
```

All build methods will reuse cache on 1st and second entry. But COPY (the 3rd layer) will trigger a layers to fork.

See example test output
```
                              FROM             RUN            COPY            RUN
docker_py-context-build: ['d6ead20d5571', 'b013f23d740f', '00fc5abc7d11', '14f4a6a4048a']
        docker_py-build: ['d6ead20d5571', 'b013f23d740f', '9a9fabca5004', '1204cd88e5ad']
   docker-compose-build: ['d6ead20d5571', 'b013f23d740f', '9a9fabca5004', '1204cd88e5ad']
   docker-context-build: ['d6ead20d5571', 'b013f23d740f', '5e34ecab6b3e', '2f5ed38e8b40']
           docker-build: ['d6ead20d5571', 'b013f23d740f', '5e34ecab6b3e', '2f5ed38e8b40']
```
You can see that 1st two layers are identical across all build methods. But the moment we introduce COPY builds divert.


Versions used
-------------
```
> docker info
Containers: 5
Images: 10
Server Version: 1.9.1
Storage Driver: aufs
 Root Dir: /var/lib/docker/aufs
 Backing Filesystem: extfs
 Dirs: 20
 Dirperm1 Supported: false
Execution Driver: native-0.2
Logging Driver: json-file
Kernel Version: 3.13.0-53-generic
Operating System: Ubuntu 14.04.2 LTS
CPUs: 1
Total Memory: 1.954 GiB
Name: mateusz.build
ID: EEQH:2YPB:QJC3:VVZQ:Q5SJ:4FJ5:HYSE:SZD7:37KE:2ABD:SMDX:ZILP
Debug mode (server): true
 File Descriptors: 14
 Goroutines: 22
 System Time: 2015-12-11T19:22:43.413412544Z
 EventsListeners: 0
 Init SHA1: 4fc7c03a06c675f115b39958c13486d53df10a14
 Init Path: /usr/lib/docker/dockerinit
 Docker Root Dir: /var/lib/docker
Username: munhitsu
Registry: https://index.docker.io/v1/
WARNING: No swap limit support
Labels:
 provider=amazonec2
```

```
> docker -v
Docker version 1.9.1, build a34a1d5
```

```
> pip freeze
appnope==0.1.0
decorator==4.0.6
docker-compose==1.5.2
docker-py==1.6.0
dockerpty==0.3.4
docopt==0.6.2
enum34==1.1.1
functools32==3.2.3.post2
gnureadline==6.3.3
ipython==4.0.1
ipython-genutils==0.1.0
jsonschema==2.5.1
path.py==8.1.2
pexpect==4.0.1
pickleshare==0.5
ptyprocess==0.5
PyYAML==3.11
requests==2.7.0
simplegeneric==0.8.1
six==1.10.0
texttable==0.8.4
traitlets==4.0.0
websocket-client==0.34.0
wheel==0.24.0

```