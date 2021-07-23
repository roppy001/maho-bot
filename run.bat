cd /d %~dp0

mkdir log
mkdir data

call env\Scripts\activate.bat

python -u command.py >> log\console.log 2>> log\error.log

pause