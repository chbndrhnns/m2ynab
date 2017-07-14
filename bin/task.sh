#!/bin/bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

. ~/.virtualenvs/m2ynab/bin/activate
/usr/local/bin/fswatch -t -1  "/Users/jo/Library/Containers/com.moneymoney-app.retail/Data/Library/Application Support/MoneyMoney/Database/MoneyMoney-Temp.sqlite"
osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Export requested...\""
sleep 10;
python $ROOT/m2ynab/ofx_manager.py
status=$?
if [ ${status} -eq 0 ]; then
    osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Export finished.\""
elif [ ${status} -eq 2 ]; then
    osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Database locked. Nothing to do.\""
else
    osascript -e "display notification \"$theDate\" with title \"m2ynab\" subtitle \"Exported NOT successful.\""
fi

