import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import distance
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Establish a connection to the SQLite database
conn = sqlite3.connect('spotify.db')

# Load the top_Tracks and random_Tracks tables into pandas dataframes
top_tracks_df = pd.read_sql_query("SELECT * from top_Tracks", conn)
random_tracks_df = pd.read_sql_query("SELECT * from random_Tracks", conn)

# List of the features to consider for clustering and similarity
features = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'mode', 'key', 'time_signature', 'popularity']

# Prompt the user to select a cluster from the top_Tracks dataframe
print("Select a cluster from the top tracks dataframe:")
print(top_tracks_df['cluster'].value_counts())
cluster = int(input("Enter a cluster number: "))
print()

# Get the cluster centroid from the top_Tracks dataframe
top_tracks_centroid = top_tracks_df[top_tracks_df['cluster'] == cluster].mean()[features].values

# Find the song in the random_Tracks dataframe that is most similar to the centroid
distances = []
for index, row in random_tracks_df.iterrows():
    point = row[features].values
    distances.append(distance.euclidean(top_tracks_centroid, point))
random_tracks_df['distance'] = distances

# Print the song in the random_Tracks dataframe that is most similar to the centroid
print("Song in random_Tracks dataframe that is most similar to the centroid:")
print(random_tracks_df.loc[random_tracks_df['distance'].idxmin()])
print()

# ToDo 



