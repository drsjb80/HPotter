import docker
from subprocess import Popen, PIPE
# NOTE: Don't forget to start up docker!
# Docker SDK Documentation: https://docker-py.readthedocs.io/en/stable/index.html

distro = "ubuntu"


# Help From: https://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout
def check_docker():
    global ver, doc_client
    not_detected, detected = "\nDocker not detected.", \
                             "\nDocker detected!"
    ver_cmd = "docker version"
    try:
        run_cmd = Popen(ver_cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = run_cmd.communicate()
        if run_cmd.returncode != 0:
            print(stderr.decode())
            print(not_detected)
            ver = 0
        else:
            print(detected)
            doc_client = docker.from_env()
            ver = 1
    except Exception as e:
        ver = 0
        print(str(e) + not_detected)


# Help From: https://docs.docker.com/engine/reference/commandline/exec/#examples
#            https://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call
#            https://stackoverflow.com/questions/46098206/how-do-i-catch-a-subprocess-call-error-with-python

def get_response(cmd, wdir):
    global dne, work_dir
    dne, base_dir, work_dir = "bash: {}: command not found".format(cmd), "base", wdir
    try:
        if ver == 1:
            if work_dir != base_dir:
                if not work_dir.__contains__("/"):
                    work_dir = "/{}".format(work_dir)
                cmd = "/bin/bash -c '{0} {1}'".format(cmd, wdir)
                output = doc_client.containers.run(distro, cmd, remove=True).decode()
            else:
                output = doc_client.containers.run(distro, cmd, remove=True).decode()
            if output.__contains__("\n"):
                output = output.replace("\n", "\r\n")
        else:
            output = dne
    except Exception as e:
        print(e)
        output = dne
    return output


def change_directories(cmd):
    global work_dir
    dne = False
    try:
        test_cmd = "/bin/bash -c '{}'".format(cmd)
        doc_client.containers.run(distro, test_cmd, remove=True)
        if ver == 1:
            if cmd != "cd ..":
                try:
                    work_dir = cmd.split(" ")[1]
                except IndexError:
                    work_dir = "base"
            else:
                work_dir = "base"
    except Exception as e:
        dne = True
        print(e)
        work_dir = "base"
    return work_dir, dne
