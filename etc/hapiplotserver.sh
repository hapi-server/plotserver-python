#!/bin/bash

source anaconda3/etc/profile.d/conda.sh; conda activate
#conda activate python3.6
conda activate python3.7
python setup.py develop
#hapiplotserver --workers 2 --port 5000 2>&1 &

# When proxied to internal network
hapiplotserver --workers 3 --port 5000 --bind 0.0.0.0 2>&1 &

#nohup hapiplotserver --workers 3 --port 5000 2>&1 &
#sleep 2
#tail -20 nohup.out &
