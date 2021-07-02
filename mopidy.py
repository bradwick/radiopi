import time
import datetime

#import pyttsx3
import requests
from gpiozero import Button
from requests.api import get


s = requests.session()

s.headers.update({"Content-Type": "application/json"})

def make_call_return_json(method, params=""):
    data = {"jsonrpc": "2.0",
            "id": "1",
            "method": method}
    if params:
        data["params"] = params
    response = s.post('http://10.0.0.10:6680/mopidy/rpc', json=data)
    return response.json()

def create_tracklist_and_shuffle():
    #engine = pyttsx3.init()
    #engine.say("Making playlist now")
    #engine.runAndWait()
    playlists_json = make_call_return_json('core.playlists.as_list')
    dow = datetime.date.today().weekday()
    # get grumpus playlist
    wanted_uri = ""
    for result in playlists_json['result']:
        if dow == 6 and result['name'] == "2000s Christian":
            wanted_uri = result['uri']
        elif result['name'] == "Grumpus Approved":
            wanted_uri = result['uri']


    # refresh grupmpus playlist, just to make sure we have any new songs that may have been added
    make_call_return_json("core.playlists.refresh", {"uri_scheme": wanted_uri})

    # get the songs in this playlists
    response = make_call_return_json("core.playlists.get_items", [wanted_uri])

    # add all of these to the playlist
    songs = response['result']
    track_uris = []

    for song in songs:
        # print(song)
        track_uris.append(song['uri'])

    make_call_return_json("core.tracklist.add", {"uris": track_uris})

    # then shuffle baby
    make_call_return_json("core.tracklist.shuffle")
    
    #loop it for for forever musics
    make_call_return_json("core.tracklist.set_repeat", ['true'])

def get_mopidy_state():
    response = make_call_return_json("core.playback.get_state")
    return response['result']


def set_mopidy_playback(mode):
    response = make_call_return_json(f"core.playback.{mode}")
    return response['result']


def skip_mopidy():
    print("Held")
    response = make_call_return_json("core.playback.next")
    return response['result']


def handle_button_press():
    print("Pressed")
    state = get_mopidy_state()
    print(state)
    if state == 'stopped':
        print("creating and starting playlist")
        create_tracklist_and_shuffle()
        set_mopidy_playback('play')
    elif state == 'paused':
        set_mopidy_playback('resume')
    else:
        set_mopidy_playback('pause')


def main():
    button = Button(3)
    button.hold_time = 2.0
    button.when_pressed = handle_button_press
    button.when_held = skip_mopidy
    counter = 0
    while True:
        time.sleep(60000)


if __name__ == '__main__':
    main()
