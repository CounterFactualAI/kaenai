#!/bin/bash
if [[ -z "$KAEN_JOB" ]]; then
    echo "Job identifier is not set" 1>&2
    exit 1
fi

source /workspace/.job/.$KAEN_JOB/env.sh

if test -f /workspace/.dojo/.$KAEN_DOJO/env.sh; then

    source /workspace/.dojo/.$KAEN_DOJO/env.sh

    if [[ "$KAEN_DOJO_STATUS" == "inactive" ]]; then
        echo "Dojo $KAEN_DOJO is inactive" 1>&2
        exit 1
    fi

    ssh -o StrictHostKeyChecking=no \
        -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
        -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
        -o LogLevel=QUIET \
        -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
        deployer@$KAEN_DOJO_MANAGER_IP 'sudo docker network rm job'$KAEN_JOB'' && \
    export KAEN_JOB_NETWORK=`ssh -o StrictHostKeyChecking=no \
        -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
        -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
        -o LogLevel=QUIET \
        -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
        deployer@$KAEN_DOJO_MANAGER_IP \
        'docker service ls --filter "name=job'$KAEN_JOB'" -q'`

    if [[ -n "$KAEN_JOB_NETWORK" ]]; then
        echo "Failed to remove job $KAEN_JOB" 1>&2
        exit 1
    else
        rm -rf /workspace/.job/.$KAEN_JOB
        exit 0
    fi

else

    echo "Dojo $KAEN_DOJO does not exist" 1>&2
    exit 1

fi   




