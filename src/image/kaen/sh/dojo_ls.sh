#!/bin/bash
for dojo in $(ls -1 -d -t $KAEN_DOJO_LS_REVERSE $(find /workspace/.dojo  -maxdepth 1 -type d))
do
    if test -f "$dojo/env.sh"; then
        source $dojo/env.sh && if [ -n "$KAEN_DOJO" ] ; then echo $KAEN_DOJO ; fi ;
    fi    
done