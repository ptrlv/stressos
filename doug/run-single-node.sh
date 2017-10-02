#!/bin/bash 

#export PYTHONPATH=$PYTHONPATH:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/rucio-clients/1.4.6/lib/python2.6/site-packages/

clusterid=$1
processid=$2
site=$3
s3_port=$4
remote_node=$5
job_time=$6
thread_count=$7
input_file=$8

#env | sort
#echo
#ulimit -n
#echo

ls -l 

hostname_short=`hostname -s`
remote_node_short=`echo $remote_node | cut -d"." -f1`
mkdir logs

#cp -v $input_file /dev/shm/${hostname_short}.object_file

((netstat_job_time = job_time + 120))

python netstat.py $netstat_job_time $remote_node $s3_port &
netstat_pid=$!

#python multiprocessing_cephs3_stress_test_v2.py $site $remote_node $job_time $thread_count $input_file

python multiprocessing_cephs3_stress_test_v3.py $site $remote_node $job_time $thread_count $input_file

wait $netstat_pip


mv -v multiprocessing_cephs3_tcp_connections_*.log logs/objectstore-netstat_${remote_node_short}_${clusterid}_${processid}.log
mv -v /dev/shm/multiprocessing_cephs3_test_${hostname_short}_${remote_node_short}.log logs/objectstore-${remote_node_short}_${clusterid}_${processid}.log && \
rm -v /dev/shm/multiprocessing_cephs3_test_${hostname_short}_${remote_node_short}.log.?

