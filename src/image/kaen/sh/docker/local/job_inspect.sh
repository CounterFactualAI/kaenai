#!/bin/bash
if [[ -z "$KAEN_JOB" ]]; then
    echo "Job identifier is not set" 1>&2
    exit 1
fi
cat /workspace/.job/.$KAEN_JOB/env.sh | grep KAEN_ | cat