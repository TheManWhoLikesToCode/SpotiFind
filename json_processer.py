import os
import json
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API credentials
client_id = 'bfea279ccc98417494c543754d8e6f17'
client_secret = '7c833503391142ccae0eda7750ada208'

# Get the list of JSON files in the directory
json_files = [file for file in os.listdir(
    'Training Data/data') if file.endswith('.json')]

# Establish a connection to the database
conn = sqlite3.connect('tracks.db')
c = conn.cursor()

# Create the "random_Tracks" table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS random_Tracks (
                id TEXT PRIMARY KEY,
                name TEXT,
                artists TEXT,
                acousticness REAL,
                danceability REAL,
                duration_ms REAL,
                energy REAL,
                instrumentalness REAL,
                liveness REAL,
                loudness REAL,
                speechiness REAL,
                tempo REAL,
                valence REAL,
                mode REAL,
                key REAL,
                time_signature REAL,
                cluster INTEGER
            )''')

# Spotipy client credentials
client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Process each JSON file
for json_file in json_files:
    # Read JSON data from file
    with open(os.path.join('Training Data/data', json_file), 'r') as file:
        data = json.load(file)

    playlists = data['playlists']

    # Process each playlist
    for playlist in playlists:
        tracks = playlist['tracks']

        # Process each track in the playlist
        for track in tracks:
            # Extract track information
            track_id = track['track_uri'].split(':')[2]
            track_name = track['track_name']
            artist_name = track['artist_name']

            # Check if the track is already in the database
            c.execute("SELECT id FROM random_Tracks WHERE id = ?", (track_id,))
            result = c.fetchone()
            if result:
                print(f'Track {track_name} is already in the database.')
                continue

            # Search for track features using the Spotify API
            results = sp.search(
                q=f'track:{track_name} artist:{artist_name}', type='track')
            if results['tracks']['items']:
                # Get the first track from the search results
                track_info = results['tracks']['items'][0]

                # Fetch the audio features of the track
                try:
                    track_info = sp.audio_features(track_info['id'])[0]

                    # Extract track features
                    acousticness = track_info['acousticness']
                    danceability = track_info['danceability']
                    duration_ms = track_info['duration_ms']
                    energy = track_info['energy']
                    instrumentalness = track_info['instrumentalness']
                    liveness = track_info['liveness']
                    loudness = track_info['loudness']
                    speechiness = track_info['speechiness']
                    tempo = track_info['tempo']
                    valence = track_info['valence']
                    mode = track_info['mode']
                    key = track_info['key']
                    time_signature = track_info['time_signature']

                except Exception as e:
                    print(
                        f'Error fetching audio features for track {track_name}: {e}')

                    # If error occurs, set default values
                    acousticness = 0.0
                    danceability = 0.0
                    duration_ms = 0.0
                    energy = 0.0
                    instrumentalness = 0.0
                    liveness = 0.0
                    loudness = 0.0
                    speechiness = 0.0
                    tempo = 0.0
                    valence = 0.0
                    mode = 0.0
                    key = 0.0
                    time_signature = 0.0

            else:
                # If no track is found, set default values
                acousticness = 0.0
                danceability = 0.0
                duration_ms = 0.0
                energy = 0.0
                instrumentalness = 0.0
                liveness = 0.0
                loudness = 0.0
                speechiness = 0.0
                tempo = 0.0
                valence = 0.0
                mode = 0.0
                key = 0.0
                time_signature = 0.0

            cluster = 0  # Replace with actual value

            # Insert track into the "random_Tracks" table
            c.execute('''INSERT INTO random_Tracks (id, name, artists, acousticness, danceability, duration_ms,
                         energy, instrumentalness, liveness, loudness, speechiness, tempo, valence, mode,
                         key, time_signature, cluster)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (track_id, track_name, artist_name, acousticness, danceability, duration_ms, energy,
                       instrumentalness, liveness, loudness, speechiness, tempo, valence, mode, key,
                       time_signature, cluster))
            print(f'Inserted track: {track_name}')
            conn.commit()


# Commit the changes and close the connection
conn.close()
