import os
import time
import spotipy
import sqlite3
import threading
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)

# Put your Spotify app credentials here
os.environ["SPOTIPY_CLIENT_ID"] = ""
os.environ["SPOTIPY_CLIENT_SECRET"] = ""
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8888/callback"

scope = "user-top-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

@app.route("/")
def index():
    return redirect(sp.auth_manager.get_authorize_url())

@app.route("/callback")
def callback():
    code = request.args.get('code')
    if code:
        token_info = sp.auth_manager.get_access_token(code)
        return redirect("/authorization_successful")
    else:
        return "Error: Missing authorization code", 400

@app.route("/authorization_successful")
def authorization_successful():
    return "Authorization successful! You can close this tab and return to your application console.", 200

def start_flask_app():
    app.run(port=8888)

def main():
    # Start Flask app on a separate thread
    threading.Thread(target=start_flask_app).start()

    # Create a new database connection and cursor
    db = sqlite3.connect('spotify.db')
    cursor = db.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS top_Tracks (
            id TEXT, name TEXT, artists TEXT, acousticness REAL, danceability REAL, 
            duration_ms INTEGER, energy REAL, instrumentalness REAL, liveness REAL, 
            loudness REAL, speechiness REAL, tempo REAL, valence REAL, mode INTEGER, 
            key INTEGER, time_signature INTEGER, popularity INTEGER, cluster INTEGER
        )
    """)

    # Pause and wait for the user to authenticate before continuing.
    while not sp.auth_manager.get_cached_token():
        print("Waiting for user authentication...")
        time.sleep(5)

    token_info = sp.auth_manager.get_cached_token()

    if token_info:
        cursor.execute("SELECT count(*) as count FROM top_Tracks")
        row = cursor.fetchone()
        if row[0] == 0:
            results = sp.current_user_top_tracks(limit=50)
            for idx, item in enumerate(results['items']):
                print(
                    f"{idx + 1}. {item['name']} by {', '.join([artist['name'] for artist in item['artists']])}")
                features = sp.audio_features(item['id'])[0]
                cursor.execute("""
                    INSERT OR IGNORE INTO top_Tracks (
                        id, name, artists, acousticness, danceability, duration_ms, energy, 
                        instrumentalness, liveness, loudness, speechiness, tempo, valence, 
                        mode, key, time_signature, popularity, cluster
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item['id'], item['name'], ', '.join(
                        [artist['name'] for artist in item['artists']]),
                    features['acousticness'], features['danceability'], features['duration_ms'],
                    features['energy'], features['instrumentalness'], features['liveness'],
                    features['loudness'], features['speechiness'], features['tempo'],
                    features['valence'], features['mode'], features['key'],
                    features['time_signature'], item['popularity'], None
                ))
            db.commit()
            print("Success! Check the console for your top tracks.")
        else:
            print("No need to fetch from Spotify API, the top_Tracks table is already populated.")

    # Don't forget to close the database connection
    db.close()

if __name__ == "__main__":
    main()
