#!/bin/bash

echo "pwd=$PWD"

# Before executing, run
#   cd ../; make install-server

source anaconda3/etc/profile.d/conda.sh; conda activate
conda activate python3.7

# When proxied to internal network
hapiplotserver --workers 5 --port 5000 --bind 0.0.0.0 #2>&1 &
