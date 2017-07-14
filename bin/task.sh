#!/bin/bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

mkdir -p ${ROOT}/log

. ~/.virtualenvs/m2ynab/bin/activate
/usr/local/bin/fswatch -t -1  "/Users/jo/Library/Containers/com.moneymoney-app.retail/Data/Library/Application Support/MoneyMoney/Database/MoneyMoney-Temp.sqlite"
echo -e "Got file system event signal. Waiting for network connection now..."

# wait for $timeout seconds that a connection happens
timeout=60
while ! lsof -t -c MoneyMone -a -i :https
do
    sleep 1
    if [ ${timeout} -eq 0 ]; then
        exit 0
    fi
    (( timeout-- ))

done

echo -e "$(date) Got network event signal."

osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Export requested. Waiting some time for new transactions...\""

# wait for $timeout seconds that a connection happens
timeout=15
while lsof -t -c MoneyMone -a -i :https
do
    sleep 1
    if [ ${timeout} -eq 0 ]; then
        exit 0
    fi
    (( timeout-- ))
done

echo -e "Starting export..."
python ${ROOT}/m2ynab/ofx_manager.py
status=$?
if [ ${status} -eq 0 ]; then
    osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Export finished.\""
    echo -e "Export ok."
    exit 0
elif [ ${status} -eq 2 ]; then
    osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Database locked. Nothing to do.\""
    echo -e "Database locked."
    exit 0
else
    osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Exported NOT successful.\""
    echo -e "Error."
    exit 1
fi