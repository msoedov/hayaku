

Hayaku -  a lightweight Python utility to generate Dockerfile and distribute tiny python tooling/apps without explicitly including sources

[![Build Status](https://travis-ci.org/msoedov/hayaku.svg?branch=master)](https://travis-ci.org/msoedov/hayaku)

## Instalation

```shell
pip install hayaku
```

## Why?
Disclaimer this repo being made just for fun in certain circumstances and have non opinionated approach for doing things.
The purpose of this is to wrap your existing tooling written in python into containers and then ship/distribute it without complicated
workflow around git repo's.


## Approach
0. Autodetect of required pypi packages to install
1. Encode py sources with base64/zip/bzip
2. Put encoded data into of generated `Dockerfile` ENV (According to POSIX we can put up to 256Mb into env variable)

```shell
ENV PY_LIB "{body}"

```

3. Extract it during docker build within the image

```shell
RUN python -c "import os,base64;b=os.getenv('PY_LIB');b=base64.b64decode(b);print(b.decode('utf-8'))" | tee app.py
```

4. Final generated Dockerfile will looks like

```shell
hayaku app.py

FROM python:3.6

MAINTAINER Erlich Bachman

WORKDIR /app

RUN pip install requests

ENV PY_LIB "aW1wb3J0IGJhc2U2NAppbXBvcnQgb3MKZnJvbSB...."
RUN python -c "import os,base64;b=os.getenv('PY_LIB');b=base64.b64decode(b);print(b.decode('utf-8'))" | tee app.py

CMD python app.py
```

which you can ship as a file, build and push image to private docker registry, etc...

## Seriosly ?
 It's up to you. It worked for my limited usecase and I hope it might be helpfull for somebody else. As it said in disclamer: this repo being made just for fun in certain circumstances and have non opinionated approach for doing such things.


## Limitation
 Does not work with multi file modules and local packages (TBD)
