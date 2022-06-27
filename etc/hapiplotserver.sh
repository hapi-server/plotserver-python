#!/bin/bash

make condaenv
source anaconda3/etc/profile.d/conda.sh; conda activate
conda activate python3.7
pip install -e .

# hapiplotserver --workers 3 --port 5000 2>&1 &

# When proxied to internal network
hapiplotserver --workers 3 --port 5000 --bind 0.0.0.0 2>&1 &
