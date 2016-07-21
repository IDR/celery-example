#!/bin/bash

OUTDIR=celery-example-output
mkdir -p "$OUTDIR"
out="$OUTDIR/$(date +%Y%m%d-%H%M%S).txt"
if [ -f "$out" ]; then
    echo "ERROR: File exists: $out" >&2
    exit 2
fi

if [ -n "$1" ]; then
    t="$1"
else
    t=$(($RANDOM % 10))
fi
date >> "$out"
echo "Sleeping for $t seconds" >> "$out"
sleep $t
date >> "$out"
