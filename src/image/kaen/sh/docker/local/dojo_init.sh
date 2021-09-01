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
EOT
chmod +x /workspace/.dojo/.$KAEN_DOJO/env.sh

docker info | grep -q 'Swarm: active' \
    && echo "KAEN_DOJO_STATUS=active #as of $(date)" >> /workspace/.dojo/.$KAEN_DOJO/env.sh