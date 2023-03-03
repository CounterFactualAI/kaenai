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

scp -q \
		-o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o TCPKeepAlive=yes \
    -o ServerAliveInterval=$KAEN_JOB_CREATE_ALIVE_INTERVAL \
    -o ServerAliveCountMax=$KAEN_JOB_CREATE_ALIVE_COUNT \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
		/workspace/.job/.$KAEN_JOB/img.pull.$KAEN_JOB.yaml \
		deployer@$KAEN_DOJO_MANAGER_IP:/tmp/img.pull.$KAEN_JOB.yaml \
&& ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
    -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
    -o TCPKeepAlive=yes \
    -o ServerAliveInterval=$KAEN_JOB_CREATE_ALIVE_INTERVAL \
    -o ServerAliveCountMax=$KAEN_JOB_CREATE_ALIVE_COUNT \
    -o LogLevel=QUIET \
    -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
    deployer@$KAEN_DOJO_MANAGER_IP \
		'IMG_PULL_JOB=$(kubectl create -o name -f /tmp/img.pull.'$KAEN_JOB'.yaml) && kubectl wait --for=condition=complete --timeout=600s $IMG_PULL_JOB && kubectl create namespace '$KAEN_JOB'' \
&& echo "KAEN_JOB_MANAGER_IP=$KAEN_DOJO_MANAGER_IP" >> /workspace/.job/.$KAEN_JOB/env.sh \
&& echo "KAEN_JOB_STATUS=created #as of $(date)" >> /workspace/.job/.$KAEN_JOB/env.sh