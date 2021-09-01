#!/bin/bash
for dojo in $(find .dojo  -maxdepth 1 -type d)
do
    if test -f "$dojo/env.sh"; then
        source $dojo/env.sh
        if [ "$KAEN_DOJO_STATUS" = "inactive" ]; then
            rm --preserve-root -r $dojo && echo $KAEN_DOJO
        fi
    fi
done