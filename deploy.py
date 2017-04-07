import os
import sys
import signal
import shutil
import logging
import pip

try:
    import yaml
except ImportError:
    pip.main(['install', 'pyyaml'])  # assure yaml is installed for read_config
    import yaml

try:
    import virtualenv
except ImportError:
    pip.main(['install', 'virtualenv'])
    import virtualenv

from env_load.env import read_env
from env_load.config import read_config

from subprocess_commands import blocking_process, detached_process

logging.basicConfig(filename='update.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def running_in_virtualenv():
    return hasattr(sys, 'real_prefix')


def main():
    if running_in_virtualenv():  # env will be deleted, can't be running within it.
        logger.info('Closing virtualenv and reopening in system python')
        detached_process(['python', os.path.realpath(__file__)])
        sys.exit()

    # set working directory to directory of file
    logger.info('Changing working directory.')
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # grab config
    logger.info('Loading config.')
    env = read_env()
    conf = read_config('flask_site/config/config.yml', env=env)
    pidfile = conf['pidfile']
    branch = conf['github']['branch']

    # kill the old process if it is running and existed
    if os.path.isfile(pidfile):
        logger.info('Killing old process.')
        with open(pidfile) as f:
            pid = f.read()
        if os.name == 'nt':  # on Windows, use more reliable taskkill
            blocking_process(['taskkill', '/F', '/PID', pid, '/T'])
        else:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except PermissionError:
                logger.warning('Encountered permission error closing old process -- assuming it is already killed.')
        os.remove(pidfile)

    # pull latest changes to local repo
    logger.info('Pulling latest info.')
    blocking_process(['git', 'pull', 'origin', branch])
    blocking_process(['git', 'checkout', branch])

    # rebuild virtualenv
    logger.info('Create virtual environment.')
    if os.path.isdir('env'):
        shutil.rmtree('env')
    out, err = blocking_process(['python', '-m', 'virtualenv', 'env'])
    venv_bin = str(out).split('python executable in ')[1].split('\\r\\n')[0].replace('\\\\', '\\')

    # install packages via pip
    logger.info('Install packages to Python at %s' % venv_bin)
    blocking_process([venv_bin, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # launch!
    logger.info('Launch')
    detached_process([venv_bin, 'start.py', env])


if __name__ == '__main__':
    main()
