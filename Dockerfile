ARG PYTHON_VERSION=3.8-alpine3.12

FROM python:3.8-alpine3.12
ENV PYTHONUNBUFFERED 1
RUN apk update &&  apk upgrade &&  apk add --no-cache bash \
    make g++ &&  rm -rf /var/cache/apk/*

WORKDIR /srv/
COPY . /srv/

RUN pip3 install -U pip && pip3 install -r /srv/requirements-dev.txt &&  rm -rf /root/.cache/pip/*


ENTRYPOINT ["python3.8"]
