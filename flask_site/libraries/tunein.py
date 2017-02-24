import requests

from flask_site import config, DEBUG

TUNEIN_URL = 'http://air.radiotime.com/Playing.ashx'
TUNEIN_CONFIG = config.get('tunein')

if (TUNEIN_CONFIG is None or TUNEIN_CONFIG.get('station_id', '') == ''
        or TUNEIN_CONFIG.get('partner_id', '') == '' or TUNEIN_CONFIG.get('partner_key', '') == ''):
    raise KeyError('TuneIn config not present in config.yml')


def update_tunein(title, artist, album, is_commercial=False):
    if DEBUG:  # don't actually send an update to TuneIn when running in debug mode
        return True
    r = requests.get(TUNEIN_URL, params={
        'partnerId': TUNEIN_CONFIG['partner_id'],
        'partnerKey': TUNEIN_CONFIG['partner_key'],
        'id': TUNEIN_CONFIG['station_id'],
        'title': title,
        'artist': artist,
        'album': album,
        'commercial': is_commercial
    })
    return r.status_code == 200
