FROM python:3-slim

MAINTAINER Peter Love "p.love@lancaster.ac.uk"

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

#ENTRYPOINT python chkbucket.py -d vault.ecloud.co.uk --profile lancs lancs-test
