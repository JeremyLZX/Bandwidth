#!/bin/bash

curr='/home/cirlab/fyp/AHAB/p4src/controller'

# Add Ports using bfrt_python
# must run run_bfshell at the directory itself
cd $SDE # go to the directory
./run_bfshell.sh -b $curr/bfrt_port.py

# Set default settings based on scripts
cd $curr
./default_settings.sh

# Add Table Entries to for the Match Action Table.
# -u is for UDP and -t is for TCP. 
# Port is ternary: port_num &&& port_mask -> port_mask = 0 to match any ports
# -v is vlink_id or commonly known as dev_port in tofino switches. 
./add_vlink_rules.py -i '25.25.40.116/32' -v 164 -u '7575&&&0' -w 0
./add_vlink_rules.py -i '25.25.40.134/32' -v 165 -u '7575&&&0' -w 0
./add_vlink_rules.py -i '25.25.40.134/32' -v 165 -t '7575&&&0' -w 0
./add_vlink_rules.py -i '25.25.40.116/32' -v 164 -t '7575&&&0' -w 0

# Since ping is neither TCP nor UDP (ICMP), we will need to add a special entry for it.
./add_vlink_rules.py -i '25.25.40.116/32' -v 164  -w 0
./add_vlink_rules.py -i '25.25.40.134/32' -v 165  -w 0

# Write to Register allows you to hardcode a value to the Register.
# In this case we want to change the threshold of a certain vlink so we can use this.
# Because the default is -n stored_thresholds which is the register we want, we do not have
# to incldue that flag.
# 10Mbits = 2000 
# ./write_to_register.py -v 6000 -i 164 -j 166

# Guranteed Flow write to register
# 1 = guranteed, 0 = normal flow
# Mapping based on per ports
# ./write_to_register.py -n guaranteed_flows -i 164 -j 165 -v 1

# Run Script to fix the Queue Size and Processing Rate
cd $SDE
./run_pd_rpc.py rpc.py