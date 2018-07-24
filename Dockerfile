FROM python:3-slim
MAINTAINER Peter Love "p.love@lancaster.ac.uk"

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python mkobjects.py -d vault.ecloud.co.uk -b plove-mko-jun4 -n 100 -m 2000000 -s 500000
#CMD python mkobjects.py -d cs3.cern.ch -b plove-mko -n 10000 -m 2000000 -s 500000
#CMD python mkobjects.py -d s3.echo.stfc.ac.uk -b plove-mko -n 100 -m 2000000 -s 500000
#CMD python mkobjects.py -d ceph-gw1.gridpp.rl.ac.uk -b plove-mko -n 10000 -m 2000000 -s 500000
#CMD python mkobjects.py -d rgw.osris.org -b testnolimit-plove -n 10000 -m 2000000 -s 500000
#CMD python mkobjects.py -d ceph-s3.mwt2.org -p 80 --insecure -b plove-mko -n 10000 -m 2000000 -s 500000
