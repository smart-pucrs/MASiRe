#! /bin/bash

echo "[MAIN_SCRIPT] ## Start main script"
SERVER="smart@192.168.1.110"
DIR_SERVER_SCRIPTS="Desktop/DisasterSimulator/experiments/temp"
PASSWORD="Samsung2013"

args_complexity="10 50 100"
args_agents="10 20"
args_steps_amount="50 100 150"
args_package_size="10 100"
args_time="10 100 10 50"

echo "[MAIN_SCRIPT] ## Copy all script to server"
sshpass -p $PASSWORD scp -r exp_scripts $SERVER:$DIR_SERVER_SCRIPTS

sshpass -p $PASSWORD ssh -tt $SERVER << EOF

    echo "[MAIN_SCRIPT] ## Create report folder"
    mkdir $DIR_SERVER_SCRIPTS/reports

    echo "[MAIN_SCRIPT] ## Run scripts"
    python3 $DIR_SERVER_SCRIPTS/process_time_pass.py $args_time
    python3 $DIR_SERVER_SCRIPTS/process_time_search.py $args_time
    python3 $DIR_SERVER_SCRIPTS/package_size_api.py $args_package_size
    python3 $DIR_SERVER_SCRIPTS/package_size_simulator.py $args_package_size
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_complexity.py $args_complexity
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_steps_amount.py $args_steps_amount
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_maps.py
    exit
EOF
python3 exp_scripts/memory_cpu_local_agents.py $args_agents &
sshpass -p $PASSWORD ssh -tt $SERVER << EOF
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_server_agents.py $args_agents
    exit
EOF

echo "[MAIN_SCRIPT] ## Copy all reports to local pc"
sshpass -p $PASSWORD scp -r $SERVER:$DIR_SERVER_SCRIPTS/reports reports
sshpass -p $PASSWORD ssh -tt $SERVER << EOF
    echo "[MAIN_SCRIPT] ## Remove scripts folde from server"
    rm -R $DIR_SERVER_SCRIPTS
    exit
EOF

echo '[MAIN_SCRIPT] ## Finished All experiments'