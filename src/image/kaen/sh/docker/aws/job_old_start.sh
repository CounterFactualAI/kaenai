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

<<<<<<< HEAD
export CMD='echo sudo docker run
=======
if [[ $KAEN_JOB_REPLICAS > 1 ]]; then
    export CMD='sudo docker service create 
        --quiet
        --tty
        --detach
        --restart-condition=none 
        --restart-max-attempts=1
        --mode replicated
        --name job'$KAEN_JOB'
        --network job'$KAEN_JOB'
        --env KAEN_RANK={{.Task.Slot}}
        --env KAEN_WORLD_SIZE='$KAEN_JOB_REPLICAS'
        --replicas='$(($KAEN_JOB_REPLICAS-1))''

    for arg in ${!KAEN_JOB_ARG_@}
    do
    CMD=$CMD'
    -e '${arg##"KAEN_JOB_ARG_"}=$(printenv $arg)
    done

    CMD=$CMD' 
    '$KAEN_JOB_IMAGE''

    ssh -o StrictHostKeyChecking=no \
        -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
        -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
        -o LogLevel=QUIET \
        -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP \
        $CMD &
fi

export CMD='sudo docker run
>>>>>>> 2762987aa5103824097df959b503e02f58c891dc
    --tty
    --network job'$KAEN_JOB'
    --ip '$KAEN_JOB_MANAGER_IP'
    --env KAEN_RANK=0
    --env KAEN_WORLD_SIZE='$KAEN_JOB_REPLICAS''

for arg in ${!KAEN_JOB_ARG_@}
do
  CMD=$CMD'
-e '${arg##"KAEN_JOB_ARG_"}=$(printenv $arg)
done

CMD=$CMD' 
 '$KAEN_JOB_IMAGE''

if [[ $KAEN_JOB_REPLICAS > 1 ]]; then
    CMD='{ '$CMD'
    && sudo docker service rm job'$KAEN_JOB' ; } 2>&1'
fi
 
ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP \
<<<<<<< HEAD
    $CMD

if (( $KAEN_JOB_REPLICAS > 1)) then;
    REPLICAS = $(($KAEN_JOB_REPLICAS - 1))

    export CMD='echo sudo docker service create
        --name job'$KAEN_JOB'
        --network job'$KAEN_JOB'
        --replicas='$REPLICAS'
        --mode replicated
        --tty
        --quiet \
        --tty \
        --detach \
        --restart-condition=none
        --restart-max-attempts=1 
        -e WORKER={{.Task.Slot}}'     
                
    for arg in ${!KAEN_JOB_ARG_@}
    do
    CMD=$CMD'
    -e '${arg##"KAEN_JOB_ARG_"}=$(printenv $arg)
    done

    CMD=$CMD' 
    '$KAEN_JOB_IMAGE''
fi
#   && ssh -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP \
#    'echo sudo docker service rm service'$KAEN_JOB''
ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO deployer@$KAEN_DOJO_MANAGER_IP \

# # ssh -i tf_rsa admin@54.88.116.68 'sudo docker service create \
# #     --name xor_job \
# #     --env REPLICAS=4 \
# #     --env MASTER_ADDR=11.0.0.3 \
# #     --env BATCH_SIZE=1 \

# # for i in 1 2 3
# # do
# #   export LAAI=$LAAI$i
# # done
# # echo $LAAI
=======
    $CMD
>>>>>>> 2762987aa5103824097df959b503e02f58c891dc
