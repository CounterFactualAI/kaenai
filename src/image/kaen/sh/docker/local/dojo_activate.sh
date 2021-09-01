#!/bin/bash
# echo docker info | grep -q 'Swarm: active' \
#     && 
echo "KAEN_DOJO_STATUS=active #as of $(date)" >> /workspace/.dojo/.$KAEN_DOJO/env.sh