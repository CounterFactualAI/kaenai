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

export CMD='sudo docker service create 
    --name hpo'$KAEN_JOB' 
    --network job'$KAEN_JOB'
    --constraint node.role==manager
    --quiet
    --tty
    --detach
    --replicas=1
    --restart-condition=none
    --restart-max-attempts=1'

for arg in ${!KAEN_JOB_ARG_@}
do
CMD=$CMD'
-e '${arg##"KAEN_JOB_ARG_"}=$(printenv $arg)
done

for arg in ${!KAEN_JOB_PORT_@}
do
CMD=$CMD'
--publish '${arg##"KAEN_JOB_PORT_"}:$(printenv $arg)
done

for arg in ${!KAEN_HPO_@}
do
CMD=$CMD'
-e '$arg'='$(printenv $arg)
done
    
CMD=$CMD'
'$KAEN_HPO_IMAGE''

ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP \
$CMD && export KAEN_HPO_MANAGER_IP=` ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
    deployer@$KAEN_DOJO_MANAGER_IP \
    'docker inspect $(docker service ps $(docker service ls --filter "name=hpo$KAEN_JOB" -q) --filter "name=hpo$KAEN_JOB" -q) --format "{{json .NetworksAttachments}}"' \
    | jq -r '.[] | select(.Network.Spec | .Name == "job'$KAEN_JOB'") | .Addresses[0]' \
    | cut -f 1 -d / `

if [[ -z "$KAEN_HPO_MANAGER_IP" ]]; then
    echo "Failed to enable hyperparameter optimization for the job $KAEN_JOB" 1>&2
    exit 1
else
    for arg in ${!KAEN_HPO_@}
    do
    echo "$arg=$(printenv $arg)" >> /workspace/.job/.$KAEN_JOB/env.sh
    done
    echo "KAEN_HPO_STATUS=enabled #as of $(date)" >> /workspace/.job/.$KAEN_JOB/env.sh    
fi
