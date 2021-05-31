# gpudash

The `gpudash` command displays a GPU utilization dashboard over the last hour.


To get started:

```
$ gpudash -h
usage: gpudash [-h] [-u NETID] [-n]

GPU utilization dashboard for the last hour

optional arguments:
  -h, --help       show this help message and exit
  -u NETID         create dashboard for a single user
  -n, --no-legend  flag to hide the legend

Utilization is the percentage of time during a sampling window (< 1 second) that
a kernel was running on the GPU. The format of each entry in the dashboard is
username:utilization (e.g., aturing:90). Utilization varies between 0 and 100%.

Examples:

  Show dashboard for the user aturing:
    $ gpudash -u aturing

  Show dashboard for all users without displaying legend:
    $ gpudash -n
```
