FROM tiangolo/uwsgi-nginx-flask:python3.7-alpine3.7
RUN apk --update add bash vim
RUN apk add --update alpine-sdk && apk add libffi-dev openssl-dev
RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip
RUN python -m pip install -U setuptools
RUN apk --update add --no-cache --virtual build-deps $DEPS
ENV STATIC_URL /static
ENV STATIC_PATH /vlansNMS/static
COPY ./requirements.txt /vlansNMS/requirements.txt
RUN pip install -r /vlansNMS/requirements.txt


