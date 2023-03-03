#!/bin/bash
if [[ -z "$KAEN_DOJO" ]]; then
    echo "Dojo identifier is not set" 1>&2
    exit 1
fi

if [[ -z "$KAEN_JOB" ]]; then
    echo "Job identifier is not set" 1>&2
    exit 1
fi

source /workspace/.dojo/.$KAEN_DOJO/env.sh

if [[ "$KAEN_DOJO_STATUS" == "inactive" ]]; then
    echo "Dojo $KAEN_DOJO is inactive" 1>&2
    exit 1
fi

mkdir -p /workspace/.job/.$KAEN_JOB
cat <<EOT >> /workspace/.job/.$KAEN_JOB/env.sh
#!/bin/bash
KAEN_JOB=$KAEN_JOB
KAEN_DOJO=$KAEN_DOJO
KAEN_JOB_IMAGE=$KAEN_JOB_IMAGE
KAEN_JOB_CREATE_ALIVE_INTERVAL=60
KAEN_JOB_CREATE_ALIVE_COUNT=12
EOT
chmod +x /workspace/.job/.$KAEN_JOB/env.sh
source /workspace/.job/.$KAEN_JOB/env.sh

CMD='sudo docker image pull '$KAEN_JOB_IMAGE'
    && sudo docker network create --driver overlay
    --attachable
    --ipam-driver default '
if [[ -n "$KAEN_JOB_SUBNET" ]]; then
    CMD=$CMD' --subnet '$KAEN_JOB_SUBNET''
fi  
CMD=$CMD' job'$KAEN_JOB''

ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o TCPKeepAlive=yes \
    -o ServerAliveInterval=$KAEN_JOB_CREATE_ALIVE_INTERVAL \
    -o ServerAliveCountMax=$KAEN_JOB_CREATE_ALIVE_COUNT \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
    deployer@$KAEN_DOJO_MANAGER_IP \
    $CMD \
&& KAEN_JOB_SUBNET=`ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
    deployer@$KAEN_DOJO_MANAGER_IP \
    'docker network inspect --format="{{range .IPAM.Config}}{{.Subnet}}{{end}}" job'$KAEN_JOB''`

if [[ -z "$KAEN_JOB_SUBNET" ]]; then
    echo "Failed to create job network job$KAEN_JOB" 1>&2
    exit 1
else
    echo "KAEN_JOB_SUBNET=$KAEN_JOB_SUBNET" >> /workspace/.job/.$KAEN_JOB/env.sh
fi

if [[ -z "$KAEN_JOB_MANAGER_IP" ]]; then
    nextip(){
        IP=$1
        IP_HEX=$(printf '%.2X%.2X%.2X%.2X\n' `echo $IP | sed -e 's/\./ /g'`)
        NEXT_IP_HEX=$(printf %.8X `echo $(( 0x$IP_HEX + 1 ))`)
        NEXT_IP=$(printf '%d.%d.%d.%d\n' `echo $NEXT_IP_HEX | sed -r 's/(..)/0x\1 /g'`)
        echo "$NEXT_IP"
    }

    export GATEWAY=`ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
    deployer@$KAEN_DOJO_MANAGER_IP \
    'docker network inspect --format="{{range .IPAM.Config}}{{.Gateway}}{{end}}" job'$KAEN_JOB''` && \
    export KAEN_JOB_MANAGER_IP=$(ipcalc $GATEWAY | grep HostMax | tr -s " " | cut -f 2 -d " ") && \
    echo "KAEN_JOB_MANAGER_IP=$KAEN_JOB_MANAGER_IP" >> /workspace/.job/.$KAEN_JOB/env.sh
else
    echo "KAEN_JOB_MANAGER_IP=$KAEN_JOB_MANAGER_IP" >> /workspace/.job/.$KAEN_JOB/env.sh
fi

echo "KAEN_JOB_STATUS=created #as of $(date)" >> /workspace/.job/.$KAEN_JOB/env.sh