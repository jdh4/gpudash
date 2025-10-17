#!/bin/bash

BASE=/home/jdh4/bin/gpus
DATA=${BASE}/data
printf -v SECS '%(%s)T' -1

curl -s 'http://vigilant2:8480/api/v1/query?query=nvidia_gpu_duty_cycle' > ${DATA}/util.${SECS}
curl -s 'http://vigilant2:8480/api/v1/query?query=nvidia_gpu_jobUid'     > ${DATA}/uid.${SECS}
curl -s 'http://vigilant2:8480/api/v1/query?query=nvidia_gpu_jobId'      > ${DATA}/jobid.${SECS}

find ${DATA} -type f -mmin +70 -exec rm -f {} \;

/usr/licensed/anaconda3/2024.10/bin/python -B ${BASE}/extract.py 2> ${BASE}/ERROR.log

# copy column files to the other login nodes
timeout 5 scp -r /scratch/.gpudash della-gpu:/scratch/
timeout 5 scp -r /scratch/.gpudash della-vis1:/scratch/
timeout 5 scp -r /scratch/.gpudash della8:/scratch/
timeout 5 scp -r /scratch/.gpudash della9:/scratch/
