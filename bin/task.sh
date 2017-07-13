#!/bin/bash

fswatch -1 -d "/Users/jo/Library/Containers/com.moneymoney-app.retail/Data/Library/Application Support/MoneyMoney/Database/"; sleep 10; python m2ynab/ofx_manager.py
