import re
import os

from hpotter.env import logger, start_shell, get_busybox, get_shell_container
from hpotter import tables

def get_string(client_socket, limit=4096, telnet=False):
    character = client_socket.recv(1)
    if not telnet:
        client_socket.send(character)

    # while there are telnet commands
    while telnet and character == b'\xff':
        # skip the next two as they are part of the telnet command
        client_socket.recv(1)
        client_socket.recv(1)
        character = client_socket.recv(1)

    string = ''
    while character not in (b'\n', b'\r'):
        if character == b'\b':      # backspace
            string = string[:-1]
        elif character == '\x15':   # control-u
            string = ''
        elif ord(character) > 127:
            logger.debug('Meta character')
            raise UnicodeError('Meta character')
        elif len(string) > limit:
            logger.debug('Too many characters')
            raise IOError('Too many characters')
        else:
            string += character.decode('utf-8')

        character = client_socket.recv(1)
        if not telnet:
            client_socket.send(character)


    if not telnet:
        client_socket.send(b'\n')

    # read the newline
    if telnet and character == b'\r':
        character = client_socket.recv(1)

    logger.debug('get_string returing ' + string.strip())
    return string.strip()

def deal_with_dots(path, workdir):
    while path.startswith('.'):
        if path == '.':
            return '/' if workdir == '' else workdir
        if path.startswith('./'):
            path = path[2:]
            continue

        # strip out last element
        workdir = re.sub(r'/[^/]*/?$', '', workdir)

        # remove front part of path
        path = path[3:] if path.startswith('../') else path[2:]

    if path.endswith('/'):
        path = path[:-1]

    if workdir == '':
        return '/'
    elif path == '':
        return workdir
    else:
        return workdir + '/' + path

def cd(command, workdir):
    directory = command.split(' ')

    # a bare cd
    if len(directory) == 1:
        return workdir

    directory = directory[1]

    if directory.startswith('.'):
        return deal_with_dots(directory, workdir)

    if directory == '/':
        return '/'

    if workdir == '/':
        return workdir + directory

    return workdir + '/' + directory 

def fake_shell(client_socket, session, connection, prompt, telnet=False):
    start_shell()

    command_count = 0
    workdir = '/'
    while command_count < 4:
        client_socket.sendall(prompt)

        try:
            command = get_string(client_socket, telnet=telnet)
            command_count += 1
        except:
            logger.debug('get_string threw an exception')
            client_socket.close()
            break

        if command == '':
            continue

        if command == 'exit':
            break

        if command.startswith('cd'):
            workdir = cd(command, workdir)

        logger.debug('Shell workdir ' + workdir)

        cmd = tables.ShellCommands(command=command, connection=connection)
        session.add(cmd)
        session.commit()
        logger.debug('Shell committed command')

        # timeout = 'timeout 1 ' if get_busybox() else 'timeout -t 1 '

        exit_code, output = get_shell_container().exec_run(command, \
            workdir=workdir)

        logger.debug('Shell exit_code ' + str(exit_code))
        logger.debug('Shell output ' + str(output))

        output = output.replace(b'\n', b'\r\n')

        if exit_code in (126, 127):
            client_socket.sendall(command.encode('utf-8') + \
                b': command not found\n')
        else:
            client_socket.sendall(output)
