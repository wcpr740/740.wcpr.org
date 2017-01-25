from functools import wraps
from flask import request


def jsonp_support(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            response = func(*args, **kwargs)
            response.set_data('%s(%s)' % (str(callback), response.get_data(as_text=True)))
            response.mimetype = 'application/javascript'
            return response
        else:
            return func(*args, **kwargs)
    return decorated_function
