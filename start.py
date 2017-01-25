from flask_site import sock, app, flask_config

if __name__ == '__main__':
    sock.run(app, debug=flask_config.get('DEBUG'), host=flask_config.get('host'), port=flask_config.get('port'))
