#!/bin/bash

DATA="/home/jdh4/bin/gpus/data"
SBASE="/scratch/.gpudash"
printf -v SECS '%(%s)T' -1

curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_duty_cycle' > ${DATA}/util.${SECS}
curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_jobUid'     > ${DATA}/uid.${SECS}
curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_jobId'      > ${DATA}/jobid.${SECS}

find ${DATA} -type f -mmin +70 -exec rm -f {} \;

/usr/licensed/anaconda3/2020.11/bin/python /home/jdh4/bin/gpus/extract.py

scp ${SBASE}/column.* tigercpu:${SBASE}
scp ${SBASE}/column.* tiger-cryoem:${SBASE}
