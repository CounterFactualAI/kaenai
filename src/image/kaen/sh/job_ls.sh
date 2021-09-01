#!/bin/bash
for job in $(ls -1 -d -t $KAEN_JOB_LS_REVERSE $(find /workspace/.job  -maxdepth 1 -type d))
do
    if test -f "$job/env.sh"; then
        source $job/env.sh && if [ -n "$KAEN_JOB" ] ; then echo $KAEN_JOB ; fi ;
    fi    
done