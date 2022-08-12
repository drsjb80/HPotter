
# HPotter
A simple to install and run Honey Pot.

[![Build Status](https://travis-ci.org/drsjb80/HPotter.svg?branch=master)](https://travis-ci.org/drsjb80/HPotter)

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
* arguments, takes a valid [ast.literal_eval](https://docs.python.org/3/library/ast.html#ast.literal_eval) input.
    * Example: 'arguments': '{"publish_all_ports":True, "detach":True, "volumes":["tmp:/tmp"]}'
### config.yml
* database, default: 'sqlite'
* database\_name, default: 'hpotter.db'
* database\_user, default: ''
* database\_password, default: ''
* database\_host, default: ''
* database\_port', default: ''
