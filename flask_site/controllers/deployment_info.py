import pendulum

from flask_site import app, config


@app.route('/deploy_info')
def deploy_info():
    uptime = pendulum.now() - config.get('start_time')
    return "Flask deployment started: %s<br>Uptime: %s" % (config.get('start_time'), uptime.in_words(locale='en_us'))
