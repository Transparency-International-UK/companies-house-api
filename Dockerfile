FROM python:3.8

COPY ./ch_api /ch_api

WORKDIR /ch_api

RUN pip install -r requirements.txt
