import os

from flask_site import sock, app, flask_config, config

pidfile = config['pidfile']

if __name__ == '__main__':
    with open(pidfile, 'w') as f:  # save PID to pidfile so that updater can use it
        f.write('%s' % os.getppid())

    sock.run(app, debug=flask_config.get('DEBUG'), log_output=flask_config.get('DEBUG'),
             host=flask_config.get('host'), port=flask_config.get('port'))
