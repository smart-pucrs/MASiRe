#! /bin/bash
SERVER="smart@192.168.1.110"

scp -r server_scripts $SERVER:Desktop/DisasterSimulator/experiments/server_scripts
ssh -tt $SERVER << EOF
    mkdir temp
    python3 Desktop/DisasterSimulator/experiments/server_scripts/step_amount.py
    rm -R Desktop/DisasterSimulator/experiments/server_scripts    
    exit
EOF
scp -r $SERVER:temp reports
ssh -tt $SERVER << EOF
    rm -R temp
    exit
EOF

echo 'Finished All experiments' 