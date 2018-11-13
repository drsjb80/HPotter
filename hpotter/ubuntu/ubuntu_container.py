import shlex
from subprocess import Popen, PIPE
from threading import Timer
# NOTE: Don't forget to start up docker!


# help from:
# https://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout
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
            start_container()
            ver = 1
    except FileNotFoundError as e:
        print(str(e))
        print(not_detected)
    finally:
        timer.cancel()


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


def start_container():
    start_cmd = "docker start ubuntu_bash"
    create_cmd = "docker run --name ubuntu_bash --rm -t ubuntu bash"
    create, run = "\nCreating ubuntu_bash...", "ubuntu_bash running!"
    container = Popen(start_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = container.communicate()
    if container.returncode != 0:
        print(stderr.decode())
        print(create)
        Popen(shlex.split(create_cmd))
        print(run)


def special_dir_handler(cmd):
    global work_dir
    if not work_dir.__contains__("/"):
        work_dir = "/" + work_dir
    exec_cmd = "docker exec -w {0} ubuntu_bash {1}".format(work_dir, cmd)
    p = Popen(exec_cmd, stdout=PIPE)
    output = p.stdout.read().decode()
    output = reformat_output(output)
    output = bad_command_handler(output)
    return output


def root_workdir_handler(cmd):
    exec_cmd = "docker exec ubuntu_bash {}".format(cmd)
    p = Popen(exec_cmd, stdin=PIPE, stdout=PIPE)
    output = p.stdout.read().decode()
    output = reformat_output(output)
    output = bad_command_handler(output)
    return output


def bad_command_handler(output):
    if output.__contains__("failed"):
        output = dne
    return output


# Help From: https://docs.docker.com/engine/reference/commandline/exec/#examples
#            https://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call
#            https://stackoverflow.com/questions/46098206/how-do-i-catch-a-subprocess-call-error-with-python

def get_ubuntu_response(cmd, wdir):
    global dne, work_dir, ver
    dne, bash = "bash: {}: command not found".format(cmd), "bash"
    work_dir = wdir
    if ver == 1:
        if work_dir != bash:
            output = special_dir_handler(cmd)
        else:
            output = root_workdir_handler(cmd)
    else:
        output = dne

    return output


def reformat_output(output):
    if output.__contains__("\n"):
        new_output = output.replace("\n", "\r\n")
    else:
        new_output = output
    return new_output
