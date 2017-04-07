import subprocess
import logging

CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008


def blocking_process(command, log=True):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if log:
        logging.debug(out)
        if err:
            logging.error(err)
    return out, err


def detached_process(command):
    subprocess.Popen(command, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True,
                     creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
