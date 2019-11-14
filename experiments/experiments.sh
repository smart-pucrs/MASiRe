#! /bin/bash

echo "[MAIN_SCRIPT] ## Start main script"
SERVER="smart@10.32.160.100"
URL="10.32.160.100"
DIR_SERVER_SCRIPTS="Desktop/DisasterSimulator/experiments/temp"
PASSWORD="Samsung2013"

args_complexity="5 10"
args_agents="5 10"
args_steps_amount="5 10"
args_package_size="5 10"
args_time_agent_complexity="5 10 5 10"

echo "[MAIN_SCRIPT] ## Copy all script to server"
sshpass -p $PASSWORD scp -r exp_scripts $SERVER:$DIR_SERVER_SCRIPTS

sshpass -p $PASSWORD ssh -tt $SERVER << EOF

    echo "[MAIN_SCRIPT] ## Create report folder"
    mkdir $DIR_SERVER_SCRIPTS/reports
    echo "[MAIN_SCRIPT] ## Run scripts"
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_complexity.py $URL $args_complexity
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_steps_amount.py $URL $args_steps_amount
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_maps.py $URL 
    python3 $DIR_SERVER_SCRIPTS/package_size_api.py $URL $args_package_size
    python3 $DIR_SERVER_SCRIPTS/package_size_simulator.py $URL $args_package_size
    python3 $DIR_SERVER_SCRIPTS/process_time_pass.py $URL $args_time_agent_complexity
    python3 $DIR_SERVER_SCRIPTS/process_time_search.py $URL $args_time_agent_complexity
    exit
EOF
python3 exp_scripts/memory_cpu_local_agents.py $URL $args_agents &
sshpass -p $PASSWORD ssh -tt $SERVER << EOF
    python3 $DIR_SERVER_SCRIPTS/memory_cpu_server_agents.py $URL $args_agents
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