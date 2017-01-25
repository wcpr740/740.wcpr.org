import json
from copy import deepcopy

import pendulum
from flask import make_response, jsonify, request
from flask_socketio import emit, join_room, leave_room, rooms

from flask_site import app, sock, config
from flask_site.libraries.jsonp_wrap import jsonp_support

NOW_PLAYING_FILE_LOC = config.get('now_playing')
SECONDS_WAIT_FOR_RECHECK = 0.5
STREAM_DELAY_SECONDS = 12


def load_now_playing_and_fix_tz():
    """ StationPlaylist is in Eastern time so scheduling can still work, but UTC is reported and needs to be fixed.

    For this fix to work, the local machine must also be in Eastern time, and must automatically update DST.

    :return: now_playing.json fixed, and now_playing.json fixed and delayed
    :rtype: dict, dict
    """
    with open(NOW_PLAYING_FILE_LOC) as f:
        now_playing_obj = json.load(f)
    start = pendulum.parse(now_playing_obj['now']['start']).subtract(hours=pendulum.now().offset_hours)
    now_playing_obj['now']['start'] = start.isoformat()

    now_playing_obj_delayed = deepcopy(now_playing_obj)
    now_playing_obj_delayed['now']['start'] = (start.add(seconds=STREAM_DELAY_SECONDS)).isoformat()

    return now_playing_obj, now_playing_obj_delayed


thread = None  # used to house async_update thread
now_playing, now_playing_delayed = load_now_playing_and_fix_tz()  # needed global so ajax and socket can both serve
has_next_grab_scheduled = False


def async_update_now_playing():
    global now_playing
    global now_playing_delayed
    global has_next_grab_scheduled  # without, will do many 1-second pulses at start until end of first song.
    sleep_time = 0

    while True:
        sock.sleep(sleep_time)  # wait for given time before grabbing next update

        new_now_playing, new_now_playing_delayed = load_now_playing_and_fix_tz()
        if new_now_playing['now']['start'] == now_playing['now']['start'] and has_next_grab_scheduled:
            # waiting for a bump to finish.
            sleep_time = SECONDS_WAIT_FOR_RECHECK
            continue

        now_playing = new_now_playing
        sock.emit('on_air', now_playing, room='no_delay', namespace='/now_playing')
        sock.sleep(STREAM_DELAY_SECONDS)  # wait for the delay period before sending the delayed emit

        now_playing_delayed = new_now_playing_delayed
        sock.emit('on_air', now_playing_delayed, room='delayed', namespace='/now_playing')

        # set wait until next check time
        elapsed_seconds = (pendulum.now() - pendulum.parse(now_playing['now']['start'])).in_seconds()
        remaining_seconds = int(now_playing['now']['len']) - elapsed_seconds
        remaining_seconds = 0 is remaining_seconds < 0
        sleep_time = remaining_seconds + SECONDS_WAIT_FOR_RECHECK
        has_next_grab_scheduled = True


def start_thread_if_necessary():
    """ Only starts async_update_now_playing if it isn't already running.

    :return:
    """
    global thread
    if thread is None:
        thread = sock.start_background_task(target=async_update_now_playing)


@app.route('/now_playing')
@jsonp_support
def on_air():
    start_thread_if_necessary()

    if 'no_delay' in request.values:
        src = now_playing
    else:
        src = now_playing_delayed

    return make_response(jsonify(src), 200)


@sock.on('connect', namespace='/now_playing')
def connect():
    start_thread_if_necessary()
    emit('connected')


@sock.on('get', namespace='/now_playing')
def get_now_playing(message=None):
    if message is None:  # default to serving delayed info, can get un-delayed info
        delay = True
    else:
        delay = message.get('delay', True)

    if delay:
        join_room('delayed')
        emit('on_air', now_playing_delayed)
    else:
        join_room('no_delay')
        emit('on_air', now_playing)


@sock.on('disconnect', namespace='/now_playing')
def disconnect():
    for r in rooms():
        leave_room(r)
