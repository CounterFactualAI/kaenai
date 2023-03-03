#!/bin/bash
if [[ -z "$KAEN_DOJO" ]]; then
    echo "Dojo identifier is not set" 1>&2
    exit 1
fi
source /workspace/.dojo/.$KAEN_DOJO/env.sh

export TF_DATA_DIR=/workspace/.dojo/.$KAEN_DOJO
export TF_IN_AUTOMATION=1

export TF_VAR_name=dojo$KAEN_DOJO
export TF_VAR_ssh_key=$(cat /workspace/.dojo/.$KAEN_DOJO/$KAEN_DOJO.pub)

cd /opt/kaen/$KAEN_BACKEND/$KAEN_PROVIDER \
    && terraform destroy -state=/workspace/.dojo/.$KAEN_DOJO/.state -auto-approve \
    && echo "KAEN_DOJO_STATUS=inactive #as of $(date)" >> /workspace/.dojo/.$KAEN_DOJO/env.sh