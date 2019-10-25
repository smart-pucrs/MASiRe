#! /bin/bash
SERVER="smart@192.168.1.110"
DIR_SCRIPTS="Desktop/DisasterSimulator/experiments/temp"
PASSWORD="Samsung2013"

python3 scripts/local_agents.py &
sshpass -p $PASSWORD scp -r scripts $SERVER:$DIR_SCRIPTS
sshpass -p $PASSWORD ssh -tt $SERVER << EOF
    mkdir temp
    python3 $DIR_SCRIPTS/server_agents.py
    rm -R $DIR_SCRIPTS    
    exit
EOF
sshpass -p $PASSWORD scp -r $SERVER:temp reports
sshpass -p $PASSWORD ssh -tt $SERVER << EOF
    rm -R temp
    exit
EOF

echo 'Finished All experiments' 