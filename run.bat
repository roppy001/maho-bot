echo off

cd /d %~dp0

mkdir log
mkdir data

python -u command.py >> log\console.log 2>> log\error.log
