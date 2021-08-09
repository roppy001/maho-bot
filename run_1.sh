#!/bin/bash

cd ~/maho-bot

# 二重起動防止

[[ $$ != `pgrep -fo "$0"`  ]] && [[ $PPID != `pgrep -fo "$0"`  ]] && echo "$0 is already running" && exit 2 

mkdir log
mkdir data

python3 -u command.py
