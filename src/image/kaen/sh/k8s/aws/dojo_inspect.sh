#!/bin/bash
if [[ -z "$KAEN_DOJO" ]]; then
    echo "Dojo identifier is not set" 1>&2
    exit 1
fi
cat /workspace/.dojo/.$KAEN_DOJO/env.sh | grep KAEN_ | cat