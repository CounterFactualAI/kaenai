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

if [[ $KAEN_JOB_REPLICAS > 1 ]]; then
    export CMD='docker image pull '$KAEN_JOB_IMAGE'
    && sudo docker service create 
        --quiet
        --tty
        --detach
        --restart-condition=none 
        --restart-max-attempts=1
        --mode replicated
        --name job'$KAEN_JOB'
        --network job'$KAEN_JOB' 
        --env KAEN_DOJO='$KAEN_DOJO'
        --env KAEN_JOB='$KAEN_JOB'
        --env KAEN_JOB_MANAGER_IP='$KAEN_JOB_MANAGER_IP'
        --env KAEN_RANK={{.Task.Slot}}
        --env KAEN_WORLD_SIZE='$KAEN_JOB_REPLICAS'
        --replicas='$(($KAEN_JOB_REPLICAS-1))''

    for arg in ${!KAEN_JOB_ARG_@}
    do
    CMD=$CMD'
    --env '${arg##"KAEN_JOB_ARG_"}=$(printenv $arg)
    done

    for arg in ${!KAEN_HPO_@}
    do
    CMD=$CMD'
    --env '${arg}=${!arg}
    done


    CMD=$CMD' 
    '$KAEN_JOB_IMAGE''

    echo $CMD
    eval $CMD
fi

export CMD='docker image pull '$KAEN_JOB_IMAGE'
    && sudo docker run
    --tty'

if [[ "$KAEN_JOB_CFG_DETACH" == "1" ]] ; then

CMD=$CMD'
--detach'

fi

CMD=$CMD'
    --network job'$KAEN_JOB'
    --ip '$KAEN_JOB_MANAGER_IP'
    --env KAEN_DOJO='$KAEN_DOJO'
    --env KAEN_JOB='$KAEN_JOB'
    --env KAEN_JOB_MANAGER_IP='$KAEN_JOB_MANAGER_IP'
    --env KAEN_RANK=0
    --env KAEN_WORLD_SIZE='$KAEN_JOB_REPLICAS''

for arg in ${!KAEN_JOB_ARG_@}
do
  CMD=$CMD'
--env '${arg##"KAEN_JOB_ARG_"}=${!arg}
done

for arg in ${!KAEN_HPO_@}
do
  CMD=$CMD'
--env '${arg}=${!arg}
done

for arg in ${!KAEN_JOB_PORT_@}
do
  CMD=$CMD'
-p '${arg##"KAEN_JOB_PORT_"}:${!arg}
done

CMD=$CMD' 
 '$KAEN_JOB_IMAGE''

if [[ $KAEN_JOB_REPLICAS > 1 ]]; then
    CMD='{ '$CMD'
    ; sudo docker service rm job'$KAEN_JOB' ; } 2>&1'
fi
echo $CMD
eval $CMD