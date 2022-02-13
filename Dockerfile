FROM python:3.9-slim

WORKDIR /usr/src

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY . .
RUN python setup.py install
WORKDIR /usr/src/games
