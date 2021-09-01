#!/bin/bash
if [[ -z "$KAEN_DOJO" ]]; then
    echo "Dojo identifier is not set" 1>&2
    exit 1
fi
source /workspace/.dojo/.$KAEN_DOJO/env.sh && \
    echo "KAEN_DOJO_STATUS=inactive #as of $(date)" >> /workspace/.dojo/.$KAEN_DOJO/env.sh