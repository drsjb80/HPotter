import re

from hpotter.env import logger, start_shell, get_busybox, get_shell_container
from hpotter import tables

def get_string(client_socket, limit=4096, telnet=False):
    character = client_socket.recv(1)
    logger.debug(ord(character))
    if not telnet:
        client_socket.send(character)

    # while there are telnet commands
    while telnet and character == b'\xff':
        # skip the next two as they are part of the telnet command
        client_socket.recv(1)
        logger.debug(ord(character))
        client_socket.recv(1)
        logger.debug(ord(character))
        character = client_socket.recv(1)
        logger.debug(ord(character))

    string = ''
    while character not in (b'\n', b'\r'):
        if character == b'\b':      # backspace
            string = string[:-1]
        elif character == '\x15':   # control-u
            string = ''
        elif ord(character) > 127:
            raise UnicodeError('meta character')
        elif len(string) > limit:
            raise IOError('too many characters')
        else:
            string += character.decode('utf-8')

        character = client_socket.recv(1)
        logger.debug(ord(character))
        if not telnet:
            client_socket.send(character)

    if not telnet:
        client_socket.send(b'\n')

    # read the newline
    if telnet and character == b'\r':
        character = client_socket.recv(1)

    return string.strip()

def fake_shell(client_socket, session, entry, prompt, telnet=False):
    start_shell()

    command_count = 0
    workdir = ''
    while command_count < 4:
        client_socket.sendall(prompt)

        try:
            command = get_string(client_socket, telnet=telnet)
            command_count += 1
        except:
            client_socket.close()
            break

        if command == '':
            continue

        if command.startswith('cd'):
            directory = command.split(' ')
            if len(directory) == 1:
                continue

            directory = directory[1]

            if directory == '.':
                continue

            if directory == '..':
                workdir = re.sub(r'/[^/]*/?$', '', workdir)
                continue

            if directory[0] != '/':
                workdir += '/'
            workdir += directory

            continue

        if command == 'exit':
            break

        cmd = tables.CommandTable(command=command)
        cmd.hpotterdb = entry
        session.add(cmd)
        session.commit()

        timeout = 'timeout 1 ' if get_busybox() else 'timeout -t 1 '

        exit_code, output = get_shell_container().exec_run(timeout + command, \
            workdir=workdir)

        output = output.replace(b'\n', b'\r\n')

        if exit_code in (126, 127):
            client_socket.sendall(command.split()[0].encode('utf-8') + \
                b': command not found\n')
        else:
            client_socket.sendall(output)
