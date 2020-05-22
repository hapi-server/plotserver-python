#!/bin/bash

source ~/.bashrc
conda activate python3.6;
python setup.py develop;
hapiplotserver --workers 4 --port 5000
