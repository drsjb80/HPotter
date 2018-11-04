from subprocess import Popen, PIPE
import time
# NOTE: Don't forget to start up docker!


def check_docker_version():
    global ver
    proc = Popen("docker version", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    proc.wait()
    (stdout, stderr) = proc.communicate()
    if proc.returncode != 0:
        print(stderr.decode())
        print("\nDocker not detected: not using ubuntu_response")
        ver = 0
    else:
        print("\nDocker detected: ubuntu_response will be used.")
        ver = 1


# As of now: can cd forward. Need to create case for cding back
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
    container = Popen(["docker", "start", "ubuntu_bash"], stdout=PIPE, stderr=PIPE)
    container.wait()
    (stdout, stderr) = container.communicate()
    run_container(container, stderr)


def run_container(ct, err):
    if ct.returncode != 0:
        print(err.decode())
        print("\nCreating ubuntu_bash...")
        Popen("docker run --name ubuntu_bash --rm -t ubuntu bash", stdout=PIPE, stderr=PIPE, stdin=PIPE)
        # Check for ubuntu_bash, if exists, skip sleep
        time.sleep(5)
        print("ubuntu_bash running!")


def special_dir_handler(cmd):
    global work_dir
    if not work_dir.__contains__("/"):
        work_dir = "/" + work_dir
    p = Popen("docker exec -w {0} ubuntu_bash {1}".format(work_dir, cmd), stdin=PIPE, stdout=PIPE)
    output = p.stdout.read().decode()
    output = change_output_data(output)
    output = bad_command_handler(output)
    return output


def root_workdir_handler(cmd):
    p = Popen("docker exec ubuntu_bash %s" % cmd, stdin=PIPE, stdout=PIPE)
    output = p.stdout.read().decode()
    output = change_output_data(output)
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
    dne = "bash: %s: command not found" % cmd
    work_dir = wdir
    if ver == 1:
        start_container()
        if work_dir != "bash":
            output = special_dir_handler(cmd)
        else:
            output = root_workdir_handler(cmd)
    else:
        output = dne

    return output


def change_output_data(output):
    if output.__contains__("\n"):
        new_output = output.replace("\n", "\r\n")
    else:
        new_output = output
    return new_output
