#! /bin/bash
SERVER="smart@192.168.1.110"
DIR_SCRIPTS="Desktop/DisasterSimulator/experiments/temp"
PASSWORD="Samsung2013"

sshpass -p $PASSWORD scp -r scripts $SERVER:$DIR_SCRIPTS
sshpass -p $PASSWORD ssh -tt $SERVER << EOF
    mkdir $DIR_SCRIPTS/reports
    python3 $DIR_SCRIPTS/package_size.py
    exit
EOF
sshpass -p $PASSWORD scp -r $SERVER:$DIR_SCRIPTS/reports reports
sshpass -p $PASSWORD ssh -tt $SERVER << EOF
    rm -R $DIR_SCRIPTS
    exit
EOF

echo 'Finished All experiments' 