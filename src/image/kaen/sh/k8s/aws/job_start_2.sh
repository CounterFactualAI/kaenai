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
# if [[ ! "$KAEN_DOJO_STATUS" == "active" ]]; then
#     echo "Dojo is not active" 1>&2
#     exit 1
# fi
if [[ -z "$KAEN_JOB_STATUS" ]]; then
    echo "Job $KAEN_JOB is not created" 1>&2
    exit 1
fi

# rm -f /workspace/.job/.$KAEN_JOB/job.$KAEN_JOB.yaml && cat <<EOF >> /workspace/.job/.$KAEN_JOB/job.$KAEN_JOB.yaml

scp -q \
		-o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o TCPKeepAlive=yes \
    -o ServerAliveInterval=$KAEN_JOB_CREATE_ALIVE_INTERVAL \
    -o ServerAliveCountMax=$KAEN_JOB_CREATE_ALIVE_COUNT \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
		/workspace/.job/.$KAEN_JOB/job.$KAEN_JOB.yaml \
		deployer@$KAEN_DOJO_MANAGER_IP:/tmp/job.$KAEN_JOB.yaml \
&& ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o TCPKeepAlive=yes \
    -o ServerAliveInterval=$KAEN_JOB_CREATE_ALIVE_INTERVAL \
    -o ServerAliveCountMax=$KAEN_JOB_CREATE_ALIVE_COUNT \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
    deployer@$KAEN_DOJO_MANAGER_IP \
		'kubectl create --namespace='$KAEN_JOB' -o name -f /tmp/job.'$KAEN_JOB'.yaml && kubectl wait --for=jsonpath="{.status.phase}"=Running --namespace '$KAEN_JOB' pod/kaen-pytorch-manager-pod && kubectl logs --follow --namespace '$KAEN_JOB' kaen-pytorch-manager-pod'

# if [[ $KAEN_JOB_REPLICAS > 1 ]]; then
#     export CMD='sudo docker image pull '$KAEN_JOB_IMAGE'
#     && sudo docker service create 
#         --quiet
#         --tty
#         --detach
#         --constraint node.role==worker
#         --restart-condition=none 
#         --restart-max-attempts=1
#         --mode replicated
#         --name job'$KAEN_JOB'
#         --network job'$KAEN_JOB' 
#         --env KAEN_JOB='$KAEN_JOB'
#         --env KAEN_DOJO='$KAEN_DOJO'
#         --env KAEN_JOB_MANAGER_IP='$KAEN_JOB_MANAGER_IP'
#         --env KAEN_RANK={{.Task.Slot}}
#         --env KAEN_WORLD_SIZE='$KAEN_JOB_REPLICAS'
#         --replicas='$(($KAEN_JOB_REPLICAS-1))''

#     for arg in ${!KAEN_JOB_ARG_@}
#     do
#     CMD=$CMD'
#     -e '${arg##"KAEN_JOB_ARG_"}=$(printenv $arg)
#     done

#     CMD=$CMD' 
#     '$KAEN_JOB_IMAGE''

#     echo $CMD

#     ssh -o StrictHostKeyChecking=no \
#         -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
#         -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
#         -o LogLevel=QUIET \
#         -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP \
#         $CMD &
# fi

# export CMD='sudo docker image pull '$KAEN_JOB_IMAGE'
#     && sudo docker run
#     --tty'

# if [[ "$KAEN_JOB_CFG_DETACH" == "1" ]] ; then

# CMD=$CMD'
# --detach'

# fi

# CMD=$CMD'
#     --network job'$KAEN_JOB'
#     --ip '$KAEN_JOB_MANAGER_IP'
#     --env KAEN_JOB='$KAEN_JOB'
#     --env KAEN_DOJO='$KAEN_DOJO'
#     --env KAEN_JOB_MANAGER_IP='$KAEN_JOB_MANAGER_IP'
#     --env KAEN_RANK=0
#     --env KAEN_WORLD_SIZE='$KAEN_JOB_REPLICAS''

# for arg in ${!KAEN_HPO_@}
# do
#   CMD=$CMD'
# --env '${arg}=${!arg}
# done

# for arg in ${!KAEN_JOB_ARG_@}
# do
#   CMD=$CMD'
# -e '${arg##"KAEN_JOB_ARG_"}=$(printenv $arg)
# done

# for arg in ${!KAEN_JOB_PORT_@}
# do
#   CMD=$CMD'
# -p '${arg##"KAEN_JOB_PORT_"}:$(printenv $arg)
# done

# CMD=$CMD' 
#  '$KAEN_JOB_IMAGE''

# if [[ $KAEN_JOB_REPLICAS > 1 ]]; then
#     CMD='{ '$CMD'
#     ; sudo docker service rm job'$KAEN_JOB' ; } 2>&1'
# fi
# echo $CMD 
# ssh -o StrictHostKeyChecking=no \
#     -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
#     -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
#     -o LogLevel=QUIET \
#     -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP \
#     $CMD