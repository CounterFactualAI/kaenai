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
KAEN_BACKEND=$KAEN_BACKEND
KAEN_PROVIDER=$KAEN_PROVIDER
KAEN_DOJO_CONNECT_TIMEOUT=$KAEN_DOJO_CONNECT_TIMEOUT #seconds
KAEN_DOJO_CONNECT_ATTEMPTS=$KAEN_DOJO_CONNECT_ATTEMPTS
EOT
chmod +x /workspace/.dojo/.$KAEN_DOJO/env.sh

export TF_DATA_DIR=/workspace/.dojo/.$KAEN_DOJO
export TF_IN_AUTOMATION=1

cd /opt/laai/$KAEN_BACKEND/$KAEN_PROVIDER \
    && terraform init -plugin-dir=/opt/laai/$KAEN_BACKEND/$KAEN_PROVIDER/.terraform/providers

ssh-keygen -P "" -f /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO && export TF_VAR_ssh_key=$(cat /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO.pub)

export TF_VAR_name=dojo$KAEN_DOJO
cd /opt/laai/$KAEN_BACKEND/$KAEN_PROVIDER \
    && terraform apply -state=/workspace/.dojo/.$KAEN_DOJO/.state -auto-approve \
    && echo KAEN_DOJO_MANAGER_IP=$(terraform output -state=/workspace/.dojo/.$KAEN_DOJO/.state -raw manager_ip_address) >> /workspace/.dojo/.$KAEN_DOJO/env.sh \
    && ssh -o StrictHostKeyChecking=no \
        -o LogLevel=QUIET \
        -i /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO \
        deployer@$KAEN_DOJO_MANAGER_IP \
        'sudo docker info' \
    && echo "KAEN_DOJO_STATUS=active #as of $(date)" >> /workspace/.dojo/.$KAEN_DOJO/env.sh