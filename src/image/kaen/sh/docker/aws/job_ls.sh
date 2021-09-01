#!/bin/bash
for job in $(find /workspace/.job  -maxdepth 1 -type d)
do
    if test -f "$job/env.sh"; then
        source $job/env.sh && if [ -n "$KAEN_JOB" ] ; then echo $KAEN_JOB ; sleep 1 ; fi ;
    fi    
done