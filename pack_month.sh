#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

FECHA=$(TZ=":Europe/Madrid" date -d 'last month' +%Y%m)

echo "Empaquetando mes: $FECHA"

LSF_FILE=$SCRIPT_DIR/lsf.txt
WORK_DIR=$SCRIPT_DIR/last_month

rclone lsf drive-vigo:/Vigo > $LSF_FILE

while read camera; do
    echo "Procesando $camera"
    echo "Descargando ficheros"
    rclone copy --include "$FECHA??.{zip,mkv}" drive-vigo:/Vigo/$camera $WORK_DIR/download
    mkdir -p $WORK_DIR/upload/$camera
    echo "Empaquetando"
    zip -q -m -j -r $WORK_DIR/upload/$camera/$FECHA.zip $WORK_DIR/download/

    echo "Eliminando ficheros de Google Drive"
    rclone delete --include "$FECHA??.{zip,mkv}" --drive-use-trash=false drive-vigo:/Vigo/$camera

    echo "Subiendo fichero empaquetado"
    rclone move $WORK_DIR/upload/$camera/$FECHA.zip drive-vigo:/Vigo/$camera
    echo
done < $LSF_FILE

echo "Finalizado"
rm $LSF_FILE
find $WORK_DIR/upload -type d -empty -delete