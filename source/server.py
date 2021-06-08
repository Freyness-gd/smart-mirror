from flask import Flask, render_template, redirect
from flask import request as flask_request
from flask_socketio import SocketIO
import random, time, requests, json, datetime, threading, webbrowser, os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="credentials/service.json"

import classes.gmail as gmail
import classes.spotify as spotify
import classes.openweather as weather
import classes.assistant as stt

from google.cloud import storage

################# GLOBAL VARIABLES #################
app = Flask(__name__)
app.config.update(
    DEBUG=False,
    SECRET_KEY = "secret")
socketio = SocketIO(app)

Gmail = gmail.GmailClient()
Spotify = spotify.SpotifyClient('spotify_username')

shutdown = False
logStatus = False
startup = False

start_time = int(round(time.time()))
################# SERVER #################
def server():
    if __name__=='__main__':
        socketio.run(app)

################# ROUTES #################
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/spotify_login')
def spotify_login():
    url = Spotify.get_url()
    return redirect(url)

@app.route('/spotify_callback/')
def get_code():
    global logStatus
    logStatus = True
    print (logStatus)
    code = flask_request.args.get('code')
    Spotify.set_token(code)
    return redirect('/new')

@app.route('/new')
def new_index():
    return render_template("new_index.html")

################# SOCKET EVENTS #################
@socketio.on('connect')
def connect():
    # do something
    if logStatus:
        print("Connect")

@socketio.on('shutdown')
def shutdown_sequence():
    global shutdown
    shutdown = True
    func = flask_request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not runnign with the Werkzeug Server')
    func()



@socketio.on('nextTrack')
def next_track():
    Spotify.next_track()

@socketio.on('pauseTrack')
def pause_track():
    Spotify.pause_track()

@socketio.on('previousTrack')
def previous_track():
    Spotify.previous_track()

@socketio.on('resumeTrack')
def resume_track():
    Spotify.resume_track()

################# UPDATE FUNCTIONS #################
def update():
    global logStatus
    global start_time
    global startup

    diffSpotify, diffGmail, diffWeather = 1, 5, 10
    timeSpotify, timeGmail, timeWeather = [start_time for _ in range(3)]

    while True:
        if shutdown:
            print("SHUTDOWN SHUTDOWN SHUTDOWN")
            return 0
        if not logStatus:
            continue

        curr_timeSpotify = int(round(time.time()))
        curr_timeGmail = int(round(time.time()))
        curr_timeWeather = int(round(time.time()))

        if not startup:
            curr_timeSpotify += 1
            curr_timeGmail += 5
            curr_timeWeather += 10
            startup = True
            print("REMOVE LOG IN")

        if (curr_timeSpotify - timeSpotify) >= diffSpotify:
            timeSpotify = curr_timeSpotify
            socketio.emit('updateSpotify', Spotify.get_current_track())

        if (curr_timeGmail - timeGmail) >= diffGmail:
            timeGmail = curr_timeGmail
            socketio.emit('updateEmail', Gmail.request_payload())

        if (curr_timeWeather - timeWeather) >= diffWeather:
            timeWeather = curr_timeWeather
            weather_data = weather.get_weather()
            if weather_data == -1:
                continue
            socketio.emit('updateTable', weather_data)


################# ASSISTANT #################
def function_controller(data):
    if data['key'] == 'exit':
        exit()
    elif data['key'] == 'sp-next':
        Spotify.next_track()
    elif data['key'] == 'sp-prev':
        Spotify.previous_track()
    elif data['key'] == 'sp-pause':
        Spotify.pause_track()
    elif data['key'] == 'sp-res':
        Spotify.resume_track()
    elif data['key'] == 'sp-play':
        artist = None
        song = None

        if data['packet'][0] != None:
            artist = data['packet'][0]
            print("Artist: " + artist)


        if data['packet'][1] != None:
            song = data['packet'][1]
            print("Song: " + song)

        Spotify.play_track(song, artist)

    else:
        print("Nothing")

def assistant():
    AssistantObj = stt.Assistant()
    while 1:
        data = AssistantObj.start()
        print(data)
        function_controller(data)


################# THREADS #################
server_thread=threading.Thread(target=server)
update_thread=threading.Thread(target=update)
assistant_thread=threading.Thread(target=assistant)

server_thread.start()
update_thread.start()
assistant_thread.start()
