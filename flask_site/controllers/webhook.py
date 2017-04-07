import hmac
import hashlib
import json

from flask import request, jsonify

from flask_site import app, config, env

from subprocess_commands import detached_process

github_config = config['github']
github_secret = github_config['webhook_secret']
deploy_branch = github_config['branch']


def validate_signature(key, body, signature):
    """ Validate the received signature against the secret key

    :param str key: secret key
    :param str body: message body
    :param str signature: received signature
    :return:
    :rtype: bool
    """
    signature_parts = signature.split('=')
    if signature_parts[0] != "sha1":
        return False
    generated_sig = hmac.new(str.encode(key), msg=body, digestmod=hashlib.sha1)
    return hmac.compare_digest(generated_sig.hexdigest(), signature_parts[1])


@app.route('/webhook_receive', methods=['POST'])
def webhook_receive():
    """ Listens for GitHub webhooks. When a push occurs on master, pull the changes and restart the server. """
    github_signature = request.headers.get('X-Hub-Signature')

    if not validate_signature(github_secret, request.get_data(), github_signature):
        return jsonify(success=False, message='Invalid GitHub signature'), 403

    event_type = request.headers.get('X-GitHub-Event')
    if event_type != 'push':
        return jsonify(success=True, message="Ignoring event, only watching for push."), 204

    payload = request.json
    if 'refs/heads' not in payload['ref']:
        return jsonify(success=True, message="Invalid payload (missing refs/heads)."), 204

    branch = payload['ref'].split('/')[2]

    if branch != deploy_branch:
        return jsonify(success=True, message="Ignored commit to branch that isn't %s." % deploy_branch), 204

    # Everything is validated, deploy new version!
    detached_process(['python', 'deploy.py', env])
    return jsonify(success=True, message="Updating"), 200
