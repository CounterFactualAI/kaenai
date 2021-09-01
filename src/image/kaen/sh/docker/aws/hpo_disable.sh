#!/bin/bash
if [[ -z "$KAEN_JOB" ]]; then
    echo "Job identifier is not set" 1>&2
    exit 1
fi
source /workspace/.job/.$KAEN_JOB/env.sh 
source /workspace/.dojo/.$KAEN_DOJO/env.sh
if [[ -z "$KAEN_DOJO" ]]; then
    echo "Dojo is unknown" 1>&2
    exit 1
fi
if [[ ! "$KAEN_DOJO_STATUS" == "active" ]]; then
    echo "Dojo is not active" 1>&2
    exit 1
fi
if [[ -z "$KAEN_JOB_STATUS" ]]; then
    echo "Job $KAEN_JOB is not created" 1>&2
    exit 1
fi

export CMD='sudo docker service rm  $(docker service ls --filter "name=hpo'$KAEN_JOB'" -q) ; exit ;'

ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP $CMD && \
    unset KAEN_HPO_MANAGER_IP && \
    cat /workspace/.job/.$KAEN_JOB/env.sh | grep -v "^KAEN_HPO_" > /workspace/.job/.$KAEN_JOB/tmp.sh && \
    mv /workspace/.job/.$KAEN_JOB/tmp.sh /workspace/.job/.$KAEN_JOB/env.sh && \
    source /workspace/.job/.$KAEN_JOB/env.sh

if [[ -n "$KAEN_HPO_MANAGER_IP" ]]; then
    echo "Failed to disable hyperparameter optimization for the job $KAEN_JOB" 1>&2
    exit 1
else
    exit 0
fi