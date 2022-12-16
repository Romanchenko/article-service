# pull official base image
#FROM python:3.8-slim-buster
FROM continuumio/anaconda3:latest

# set work directory
WORKDIR /usr/src/app

# copy requirements file
COPY ./requirements.txt /usr/src/app/requirements.txt

# install dependencies
#RUN set -eux \
#    && apk add --no-cache --virtual .build-deps build-base \
#        libressl-dev libffi-dev gcc musl-dev python3-dev \
#    && pip install --upgrade pip setuptools wheel \
#    && pip install -r /usr/src/app/requirements.txt \
#    && rm -rf /root/.cache/pip

RUN apt-get update && apt-get install -y build-essential python3-dev
RUN pip install python-dev-tools --upgrade


RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/src/app/requirements.txt \
    && rm -rf /root/.cache/pip
RUN python -m nltk.downloader stopwords
RUN python -m spacy download en_core_web_sm
RUN conda install -c pytorch faiss-cpu
# copy project
ADD app /usr/src/app/app