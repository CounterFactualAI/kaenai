#!/bin/bash
if [[ -z "$KAEN_DOJO" ]]; then
    echo "Dojo identifier is not set" 1>&2
    exit 1
fi
if [[ -z "$KAEN_BACKEND" ]]; then
    echo "Backend is not set" 1>&2
    exit 1
fi
if [[ -z "$KAEN_PROVIDER" ]]; then
    echo "Provider is not set" 1>&2
    exit 1
fi

mkdir -p /workspace/.dojo/.$KAEN_DOJO 

cat <<EOT >> /workspace/.dojo/.$KAEN_DOJO/env.sh
#!/bin/bash
KAEN_DOJO=$KAEN_DOJO
KAEN_DOJO_VERSION=$KAEN_VERSION
KAEN_DOJO_STATUS=created #as of $(date)
KAEN_DOJO_GPU=$KAEN_DOJO_GPU
KAEN_DOJO_WORKER_INSTANCES=$KAEN_DOJO_WORKER_INSTANCES
KAEN_DOJO_WORKER_INSTANCE_TYPE=$KAEN_DOJO_WORKER_INSTANCE_TYPE
KAEN_DOJO_MANAGER_INSTANCES=$KAEN_DOJO_MANAGER_INSTANCES
KAEN_DOJO_MANAGER_INSTANCE_TYPE=$KAEN_DOJO_MANAGER_INSTANCE_TYPE
KAEN_DOJO_VOLUME_SIZE=$KAEN_DOJO_VOLUME_SIZE
KAEN_BACKEND=$KAEN_BACKEND
KAEN_PROVIDER=$KAEN_PROVIDER
KAEN_DOJO_CONNECT_TIMEOUT=$KAEN_DOJO_CONNECT_TIMEOUT #seconds
KAEN_DOJO_CONNECT_ATTEMPTS=$KAEN_DOJO_CONNECT_ATTEMPTS
EOT
chmod +x /workspace/.dojo/.$KAEN_DOJO/env.sh

export TF_DATA_DIR=/workspace/.dojo/.$KAEN_DOJO
export TF_IN_AUTOMATION=1

cd /opt/kaen/$KAEN_BACKEND/$KAEN_PROVIDER \
    && terraform init -plugin-dir=/opt/kaen/$KAEN_BACKEND/$KAEN_PROVIDER/.terraform/providers

ssh-keygen -P "" -f /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO && export TF_VAR_ssh_key=$(cat /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO.pub)

export TF_VAR_name=dojo$KAEN_DOJO
export TF_VAR_gpu=$KAEN_DOJO_GPU
export TF_VAR_instances=$KAEN_DOJO_WORKER_INSTANCES
export TF_VAR_worker_instance_type=$KAEN_DOJO_WORKER_INSTANCE_TYPE
export TF_VAR_manager_instances=$KAEN_DOJO_MANAGER_INSTANCES
export TF_VAR_manager_instance_type=$KAEN_DOJO_MANAGER_INSTANCE_TYPE
export TF_VAR_volume_size=$KAEN_DOJO_VOLUME_SIZE

cd /opt/kaen/$KAEN_BACKEND/$KAEN_PROVIDER \
    && terraform apply -state=/workspace/.dojo/.$KAEN_DOJO/.state -auto-approve \
    && echo KAEN_DOJO_MANAGER_IP=$(terraform output -state=/workspace/.dojo/.$KAEN_DOJO/.state -raw manager_ip_address) >> /workspace/.dojo/.$KAEN_DOJO/env.sh \
    && ssh \
        -o ConnectTimeout=$KAEN_DOJO_CONNECT_TIMEOUT \
        -o ConnectionAttempts=$KAEN_DOJO_CONNECT_ATTEMPTS \
        -o StrictHostKeyChecking=no \
        -o LogLevel=QUIET \
        -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
        deployer@$KAEN_DOJO_MANAGER_IP \
        'sudo docker info' \
    && echo "KAEN_DOJO_STATUS=active #as of $(date)" >> /workspace/.dojo/.$KAEN_DOJO/env.sh