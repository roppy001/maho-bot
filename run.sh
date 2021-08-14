#!/bin/bash

cd ~/maho-bot

mkdir log
mkdir data

./run_1.sh 1>>log/console.log 2>>log/error.txt &

