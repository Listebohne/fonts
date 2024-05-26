from flask import Flask, redirect, request, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
import threading

songName = 'NONE'
artistName = 'NONE'

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Verwende einen sicheren zufälligen Schlüssel
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# Deine Spotify API Zugangsdaten
client_id = 'e0610fc933ce4474b9409df366d42996'
client_secret = 'e0713ea7d12e4b118a9a6d8739f9e201'
redirect_uri = 'http://localhost:5000/callback'

# Scopes für den Zugriff auf Spotify-Daten
scope = 'user-read-playback-state'

sp_oauth = SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=redirect_uri,
                        scope=scope)

# Globale Variable für Tokeninformationen
token_info = None


def update_current_song():
    global songName
    global artistName

    while True:
        global token_info
        if token_info:
            sp = spotipy.Spotify(auth=token_info['access_token'])
            current_track = sp.current_playback()
            if current_track and current_track['is_playing']:
                track = current_track['item']
                artist_names = ", ".join([artist['name'] for artist in track['artists']])
                track_name = track['name']
                songName = f"{track_name}"
                artistName = f"{artist_names}"
                #print(f"Updated song: {track_name} by {artist_names}")
                print(songName)
                print(artistName)
            else:
                print("No track currently playing")
        time.sleep(2)


def get_token():
    global token_info
    if not token_info:
        return None

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if is_expired:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info


@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    global token_info
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    threading.Thread(target=update_current_song, daemon=True).start()
    return "Authorization successful. The song information is being updated in the background."


if __name__ == '__main__':
    app.run(debug=True)
