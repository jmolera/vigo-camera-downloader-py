#!/bin/bash

FECHA=$(TZ=":Europe/Madrid" date -d 'last month' +%Y%m)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

$SCRIPT_DIR/pack_month.sh $FECHA