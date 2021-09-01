#!/bin/bash
if [[ -z "$KAEN_DOJO" ]]; then
    echo "Dojo identifier is not set" 1>&2
    exit 1
fi
source /workspace/.dojo/.$KAEN_DOJO/env.sh


ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=5 \
    -o ConnectionAttempts=1 \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
    deployer@$KAEN_DOJO_MANAGER_IP \
    'sudo docker info' \
    && echo "KAEN_DOJO_STATUS=active #as of $(date)" >> /workspace/.dojo/.$KAEN_DOJO/env.sh    