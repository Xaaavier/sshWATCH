# sshWATCH

## Disclamer

The tool presented here has no other purpose than to train me to write Python scripts.
Even if the tool is functional under the conditions in which I tested it, I do not recommend its use in production without checks and adaptations!

## Description

This script is a tool for monitoring, in real time, SSH connections made on a server.
For each new login, it:
- created a table entry to mark the connection (using the IP address)
- Sends an alert email notifying the administrator of the new connection (email containing the original IP address of the connection, as well as the associated country).
At each disconnection, the entry created will be deleted in order to allow a new alert during subsequent connections.

To operate, the following applications must be available:
- email

## How To

Get the entire contents of this repository on a machine:

> git clone https://github.com/Xaaavier/sshWATCH.git

> wget https://github.com/Xaaavier/sshWATCH/archive/refs/heads/main.zip && unzip main.zip

Edit the etc/sshwatch file to fill in:
- HOSTNAME = YOUR.HOSTNAME.HERE
-RECEIVER=YOUR.ADMINEMAIL.HERE
Then move it to "/etc/"
Move sshwatch.py to "/usr/local/bin"