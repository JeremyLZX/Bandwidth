#!/bin/bash
#source set_pythonpath.sh
./add_mirror_session.py -p 196

# 100000 -> 1.5Gbps
./update_capacities.py -f 600000
# ./update_capacities.py -c 64500 -v -O '164,165' -o
./add_lpf_rules.py -d 4e6 -s 3 -n rate_estimator
./add_lpf_rules.py -d 16e6 -s 5 -n link_rate_tracker
./add_delta_rules.py -d 4
