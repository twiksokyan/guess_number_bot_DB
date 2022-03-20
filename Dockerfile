FROM python:latest

WORKDIR /src
COPY requerments.txt /src
RUN pip install -r requerments.txt
COPY . /src