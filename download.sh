#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

TZ=":Europe/Madrid" python3 $SCRIPT_DIR/main.py