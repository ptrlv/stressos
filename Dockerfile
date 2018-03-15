FROM python:3-slim

MAINTAINER Peter Love "p.love@lancaster.ac.uk"

WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

ENTRYPOINT python3 chkbucket.py -d vault.ecloud.co.uk --profile lancs lancs-test
