#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

FECHA=$(TZ=":Europe/Madrid" date -d 'yesterday' +%Y%m%d)

for d in $SCRIPT_DIR/imagenes/*/; do
    cd $d$FECHA/
    ffmpeg -loglevel quiet -framerate 2 -pattern_type glob -i '*.jpg' -codec copy $d$FECHA.mkv
    zip -q -m -j -r $d$FECHA.zip $d$FECHA/ -i '*.jpg'
done

rclone move $SCRIPT_DIR/imagenes/ drive-vigo:/Vigo --include "*.zip" --include "*.mkv"

find $SCRIPT_DIR/imagenes -type d -empty -delete