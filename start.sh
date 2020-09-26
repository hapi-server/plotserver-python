#!/bin/bash

source ~/.bashrc
conda activate python3.6
python setup.py develop
nohup hapiplotserver --workers 3 --port 5000 2>&1 &
sleep 2
tail -20 nohup.out &
