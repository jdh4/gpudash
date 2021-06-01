# this script reads three json files and extracts gpu utilization data

import os
import json
import csv
import subprocess
from glob import glob
from datetime import datetime
from socket import gethostname

num_columns = 7

host = gethostname()
if host.startswith("della"):
  comp_nodes_base = "della-i14g"
  nodelist = [comp_nodes_base + str(g) for g in range(1, 21)]
  gpus_per_node = 2
  BASE = "/home/jdh4/bin/a100"
  SBASE = "/scratch/.gpudash"
elif "tigercpu" in host or "tigergpu" in host:
  comp_nodes_base = "tiger-i"
  nodelist = [comp_nodes_base + str(i) + 'g' + str(j+1) for i in range(19, 24) for j in range(16)]
  gpus_per_node = 4
  BASE = "/home/jdh4/bin/p100"
  SBASE = "/scratch/.gpudash"
elif "traverse" in host:
  comp_nodes_base = "traverse-k0"
  nodelist = [comp_nodes_base + str(i) + 'g' + str(j+1) for i in [1, 2, 4, 5] for j in range(12)]
  nodelist.remove("traverse-k05g11"); nodelist.remove("traverse-k05g12")
  gpus_per_node = 4
  BASE = "/home/jdh4/bin/v100"
  SBASE = "/scratch/.gpudash"
else:
  print(f"{host} is unknown. Try running on della-gpu, tigercpu, tigergpu or traverse. Exiting ...")
  sys.exit(0)

###########################################################################
# convert uid to netid
###########################################################################
# $ getent passwd | awk -F":" '{print $3","$1}' > master.uid
with open(f"{BASE}/master.uid") as infile:
  reader = csv.reader(infile)
  uid2user = {rows[0]:rows[1] for rows in reader}

# initialize dictionary
# tuple is (username, util, jobid)
stats = {}
for node in nodelist:
  for gpu_index in range(gpus_per_node):
    stats[(node, str(gpu_index))] = ("OFFLINE", "N/A", "N/A")

# get latest timestamp
timestamp        = str(max([int(filename.split(".")[1]) for filename in glob(f"{BASE}/data/util.*")]))
timestamp_uid    = str(max([int(filename.split(".")[1]) for filename in glob(f"{BASE}/data/uid.*")]))
timestamp_jobid  = str(max([int(filename.split(".")[1]) for filename in glob(f"{BASE}/data/jobid.*")]))
assert (timestamp == timestamp_uid and timestamp == timestamp_jobid)

###########################################################################
# nvidia_gpu_duty_cycle
###########################################################################
#{"metric":{"__name__":"nvidia_gpu_duty_cycle",
#           "cluster":"della",
#           "instance":"della-i12g1:9445",
#           "job":"Della GPU Nodes",
#           "minor_number":"0",
#           "name":"NVIDIA A100-PCIE-40GB",
#           "uuid":"GPU-ff986cfe-bbb2-163f-b618-719e809ff71c"},
#"value":[1621785602.02,"0"]},
#{"metric":{"__name__":"nvidia_gpu_duty_cycle",
#           "cluster":"della",
#           "instance":"della-i12g1:9445",
#           "job":"Della GPU Nodes",
#           "minor_number":"1",
#           "name":"NVIDIA A100-PCIE-40GB",
#           "uuid":"GPU-3348bc6f-b6b9-6190-9542-d7e98c64b5e8"},
#"value":[1621785602.02,"0"]}

with open(f"{BASE}/data/util.{timestamp}") as fp:
  data = json.load(fp)
if data["status"] == "success":
  for result in data["data"]["result"]:
    hostname = result["metric"]["instance"].split(":")[0]
    if hostname.startswith(comp_nodes_base) and hostname in nodelist:
      gpu_index = result["metric"]["minor_number"]
      util = result["value"][1]
      stats[(hostname, gpu_index)] = (stats[(hostname, gpu_index)][0], util, stats[(hostname, gpu_index)][2])

###########################################################################
# nvidia_gpu_jobUid
###########################################################################
#{"metric":{"__name__":"nvidia_gpu_jobUid",
#           "cluster":"della",
#           "instance":"della-i12g1:9445",
#           "job":"Della GPU Nodes",
#           "minor_number":"0",
#           "name":"NVIDIA A100-PCIE-40GB",
#           "uuid":"GPU-ff986cfe-bbb2-163f-b618-719e809ff71c"},
#"value":[1621785602.064,"0"]},
#{"metric":{"__name__":"nvidia_gpu_jobUid",
#           "cluster":"della",
#           "instance":"della-i12g1:9445",
#           "job":"Della GPU Nodes",
#           "minor_number":"1",
#           "name":"NVIDIA A100-PCIE-40GB",
#           "uuid":"GPU-3348bc6f-b6b9-6190-9542-d7e98c64b5e8"},
#"value":[1621785602.064,"0"]}

def getent_passwd(uid):
  cmd = f"getent passwd {uid}"
  output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
  line = output.stdout.decode("utf-8")
  if line.count(":") > 0:
    username = line.split(":")[0]
    uid2user[uid] = username
    return username
  else:
    return "UNKNOWN"

with open(f"{BASE}/data/uid.{timestamp}") as fp:
  data = json.load(fp)
if data["status"] == "success":
  for result in data["data"]["result"]:
    hostname = result["metric"]["instance"].split(":")[0]
    if hostname.startswith(comp_nodes_base) and hostname in nodelist:
      gpu_index = result["metric"]["minor_number"]
      uid = result["value"][1]
      user = uid2user[uid] if uid in uid2user else getent_passwd(uid)
      stats[(hostname, gpu_index)] = (user, stats[(hostname, gpu_index)][1], stats[(hostname, gpu_index)][2])

###########################################################################
# nvidia_gpu_jobId
###########################################################################
#{"metric":{"__name__":"nvidia_gpu_jobId",
#           "cluster":"della",
#           "instance":"della-i12g1:9445",
#           "job":"Della GPU Nodes",
#           "minor_number":"0",
#           "name":"NVIDIA A100-PCIE-40GB",
#           "uuid":"GPU-ff986cfe-bbb2-163f-b618-719e809ff71c"},
#"value":[1622319602.396,"34792230"]},
#{"metric":{"__name__":"nvidia_gpu_jobId",
#           "cluster":"della",
#           "instance":"della-i12g1:9445",
#           "job":"Della GPU Nodes",
#           "minor_number":"1",
#           "name":"NVIDIA A100-PCIE-40GB",
#           "uuid":"GPU-3348bc6f-b6b9-6190-9542-d7e98c64b5e8"},
#"value":[1622319602.396,"0"]}

with open(f"{BASE}/data/jobid.{timestamp}") as fp:
  data = json.load(fp)
if data["status"] == "success":
  for result in data["data"]["result"]:
    hostname = result["metric"]["instance"].split(":")[0]
    if hostname.startswith(comp_nodes_base) and hostname in nodelist:
      gpu_index = result["metric"]["minor_number"]
      jobid = result["value"][1]
      stats[(hostname, gpu_index)] = (stats[(hostname, gpu_index)][0], stats[(hostname, gpu_index)][1], jobid)

###########################################################################
# roll column files and write output
###########################################################################

# roll the column files
for i in range(2, num_columns + 1):
  curfile = f"{SBASE}/column.{i}"
  if os.path.isfile(curfile):
    os.rename(curfile, f"{SBASE}/column.{i-1}")

# write utilization data
with open(f"{BASE}/utilization.json", "a") as f, open(f"{SBASE}/column.7", "w") as g:
  for u, v in stats.items():
    hostname, gpu_index = u
    username, util, jobid = v
    d = {"timestamp":timestamp, "host":hostname, "index":gpu_index, "user":username, "util":util, "jobid":jobid}
    json.dump(d, f); f.write("\n")
    json.dump(d, g); g.write("\n")