import os

from env_load.yaml_ordered_loader import ordered_load


def read_config(filename, env=None):
    """ Open the YAML config if it exists, and load an environment if specified.

    :param str filename: file name and location of config file to read
    :param str env: env to read from config file. If None specified, returns entire config file
    :return: the loaded config `dict`
    :rtype: dict
    """
    if not os.path.isfile(filename):
        raise IOError('The file %s is not found' % filename)

    with open(filename, 'r') as f:
        doc = ordered_load(f)

    if env is None:
        return doc

    if env not in doc:
        raise ValueError("Specified environment doesn't exist in config file")
    return doc[env]


__all__ = ['read_config']
