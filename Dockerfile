FROM python:3.9-slim

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .
RUN python setup.py install
WORKDIR /usr/src/games
