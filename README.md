
# HPotter
A simple to install and run Honey Pot.

[![Build Status](https://travis-ci.com/The-Mostly-Muggles/HPotter.svg?branch=dev)](https://travis-ci.com/The-Mostly-Muggles/HPotter)

## Running and developing

To install the necessary packages, do:

    pip install -r requirements.txt

To run the honeypot itself, do:

    python3 -m src

### containers.yml
A list of one or more of the following.
* container, the name of the Docker container to run
* listen\_address, default: 0.0.0.0
* listen\_port, the port number.
* request\_length, how many bytes requests are allowed to be, default: 4096.
* response\_length, how many bytes responses are allowed to be, default: 4096.
* request\_commands, how many request commands (between delimiters), default: 10.
* response\_commands, how many response commands (between delimiters), default: 10.
* request\_delimiters, a list of delimiters between request commands, default: - \n\r.
* response\_delimiters, a list of delimiters between response commands, default: - \n\r.
* socket\_timeout, how many seconds of inactivity before closing socket. 
* threads, how many concurrent threads for this type of container, default: Python's default.

### config.yml
* database, default: 'sqlite'
* database\_name, default: 'hpotter.db'
* database\_user, default: ''
* database\_password, default: ''
* database\_host, default: ''
* database\_port', default: ''

### src/chain.py
This file dynamically sets firewall rules while the honey pot is running.
By default it opens ssh port 22. To change this, edit the port number on 
line 153 in the 'add_ssh_rules' function.
On the device you wish to connect to, you must edit the sshd_config file:
```
    <nano/vim/etc> /etc/ssh/sshd_config
```
In the file, locate the line; 
```
    Port 22
```
which may be commented out. Change this value to any port number you wish.
(You are recommended to pick a port between 1024 - 49152 as these are lesser known ports)

Restart the ssh daemon with 
```
    sudo systemctl restart sshd
```

Now, when you wish to connect to the device:
```
    ssh user@ip_address -p <port number>
```

You may also wish to specify your local subnet in chain.py
You can find this on line 169 in the 'add_ssh_rules' function.
```
    #'src':'192.168.0.0/16', \
```
Change the private ip range to suit your own local network.