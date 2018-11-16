import docker
from subprocess import Popen, PIPE
from threading import Timer
# NOTE: Don't forget to start up docker!
# Docker SDK Documentation: https://docker-py.readthedocs.io/en/stable/index.html

doc_client = docker.from_env()
ver = 1
distro = "ubuntu"


# Help From: https://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout
def check_docker_version():
    global ver
    not_detected, detected = "\nDocker not detected: not using ubuntu_response", \
                             "\nDocker detected: Starting Ubuntu_Bash..."
    ver_cmd = "docker version"
    timeout = 5
    proc = Popen(ver_cmd, stdout=PIPE, stderr=PIPE)
    timer = Timer(timeout, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            print(stderr.decode())
            print(not_detected)
            ver = 0
        else:
            print(detected)
            ver = 1
    except FileNotFoundError as e:
        print(str(e))
        print(not_detected)
    finally:
        timer.cancel()


# Help From: https://docs.docker.com/engine/reference/commandline/exec/#examples
#            https://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call
#            https://stackoverflow.com/questions/46098206/how-do-i-catch-a-subprocess-call-error-with-python

def get_container_response(cmd, wdir):
    global dne, work_dir, ver
    dne, bash, work_dir = "bash: {}: command not found".format(cmd), "bash", wdir
    if ver == 1:
        if work_dir != bash:
            if not work_dir.__contains__("/"):
                work_dir = "/" + work_dir
            cmd = "/bin/bash -c " + "'" + cmd + " " + wdir + "'"
            output = doc_client.containers.run(distro, cmd).decode()
        else:
            output = doc_client.containers.run(distro, cmd).decode()
        output = reformat_output(output)
        output = bad_command_handler(output)
    else:
        output = dne

    return output


def reformat_output(output):
    if output.__contains__("\n"):
        new_output = output.replace("\n", "\r\n")
    else:
        new_output = output
    return new_output


def cd_command_handler(cmd, chan):
    global work_dir, ver
    if ver == 1:
        if cmd != "cd ..":
            try:
                work_dir = cmd.split(" ")[1]
                print(work_dir)
            except IndexError:
                if cmd == "cd":
                    chan.send("\r\n")
                else:
                    chan.send("\r\nbash: " + cmd + ": command not found")
                work_dir = "bash"
        else:
            work_dir = "bash"
    return work_dir


def bad_command_handler(output):
    if output.__contains__("failed"):
        output = dne
    return output
