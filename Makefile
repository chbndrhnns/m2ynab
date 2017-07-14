CWD:=$(shell pwd)

TASK:=de.chbndrhnns.m2ynab.plist

install:
	cd ~/Library/LaunchAgents; ln -f -s $(CWD)/$(TASK) $(TASK); cd $(CWD)
	launchctl load -w ~/Library/LaunchAgents/$(TASK)

uninstall: stop
	launchctl unload -w ~/Library/LaunchAgents/$(TASK)
	cd ~/Library/LaunchAgents; (rm $(TASK) || true)

start:
	launchctl start $(TASK) || true
	launchctl list | grep m2ynab | awk '{ print $2}'

stop:
	launchctl stop $(TASK) || true


