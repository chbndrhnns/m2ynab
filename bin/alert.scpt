#!/usr/bin/osascript
property i_The_Sender : "johannes@rueschel.de"
property theAddress2 : "code@rueschel.de"
set userNAME to ""
tell application "System Events"
    set userNAME to full name of current user
end tell
property theSubject : "*** m2ynab failure report ***"

set tm to do shell script "/usr/bin/syslog -F '$Time $Message' -k Sender com.apple.backupd -k Time ge -59m | tail -n 3"

if tm contains "failed" then
    set otherLog to do shell script "/usr/bin/syslog -F '$Time $Message' -k Sender com.apple.backupd-helper -k Time ge -59m | tail -n 20"
    tell application "Mail"
        set newMessage to make new outgoing message with properties {subject:(theSubject & userNAME), content:tm & return & otherLog}
        tell newMessage

            set visible to false
            set sender to i_The_Sender
            make new to recipient at end of to recipients with properties {address:theAddress2}

            send --<<<<---------------- change save to send to send or send to save to save in drafts

        end tell
    end tell

end if
