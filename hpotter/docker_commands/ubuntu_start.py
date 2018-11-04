from subprocess import *


# Help From: https://docs.docker.com/engine/reference/commandline/exec/#examples
#            https://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call

def pass_command(workdir, cmd):
    dne = "bash: %s: command not found" % cmd

    # Possibly change later, not sure if Py can catch exceptions from docker (like OCI)
    try:
        call("docker start ubuntu_bash")
    except:
        print("Creating container now...")
        call("docker run --name ubuntu_bash --rm -i -t ubuntu bash")

    if workdir != "bash":
        # Remove later, for testing purposes
        if not workdir.__contains__("/"):
            workdir = "/" + workdir
        p = Popen("docker exec -w {0} ubuntu_bash {1}".format(workdir, cmd), stdin=PIPE, stdout=PIPE)
        output = str(p.stdout.read().decode())
        # call("docker exec -w {0} ubuntu_bash {1}".format(workdir, cmd))
    else:
        p = Popen("docker exec ubuntu_bash %s" % cmd, stdin=PIPE, stdout=PIPE)
        output = str(p.stdout.read().decode())
        if output.__contains__("OCI runtime exec failed:"):
            output = dne

    return output
