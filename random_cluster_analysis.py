import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from scipy.spatial import distance
import numpy as np

def run_music_cluster_analysis():
    # Connect to the SQLite database
    conn_spotify = sqlite3.connect("./spotify.db")
    conn_tracks = sqlite3.connect("./tracks.db")

    # Load the data into a pandas DataFrame
    df_spotify = pd.read_sql_query("SELECT * FROM top_Tracks", conn_spotify)
    df_tracks = pd.read_sql_query("SELECT * FROM random_Tracks", conn_tracks)

    # Close the connections
    conn_spotify.close()
    conn_tracks.close()

    # Extract the features from the DataFrame
    features_spotify = df_spotify.drop(['id', 'name', 'artists'], axis=1)
    features_tracks = df_tracks.drop(['id', 'name', 'artists'], axis=1)

    # Normalize the features
    scaler = StandardScaler()
    features_spotify_scaled = scaler.fit_transform(features_spotify)
    features_tracks_scaled = scaler.fit_transform(features_tracks)  # Use the same scaler

    # Combine the data from both tables
    combined_features_scaled = np.concatenate((features_spotify_scaled, features_tracks_scaled), axis=0)

    # Compute the t-SNE embedding on the combined data
    tsne = TSNE(n_components=2, random_state=0, init='random', learning_rate=200)
    embedding_combined = tsne.fit_transform(combined_features_scaled)

    # Split the combined embedding back into separate embeddings for spotify and tracks data
    embedding_spotify = embedding_combined[:len(df_spotify)]
    embedding_tracks = embedding_combined[len(df_spotify):]

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=5, random_state=0).fit(embedding_spotify)

    # Assign each data point to a cluster
    df_spotify['cluster'] = kmeans.labels_
    df_tracks['cluster'] = kmeans.predict(embedding_tracks)  # Predict clusters for the tracks data

    # Extract the centroids
    centroids = kmeans.cluster_centers_

    # Create a color map for the clusters
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # Plot the t-SNE embedding with clusters
    plt.figure(figsize=(10, 10))

    for cluster in range(5):
        cluster_data_spotify = embedding_spotify[df_spotify['cluster'] == cluster]
        plt.scatter(cluster_data_spotify[:, 0], cluster_data_spotify[:, 1], c=colors[cluster], label=f"Cluster {cluster}")

        cluster_data_tracks = embedding_tracks[df_tracks['cluster'] == cluster]
        plt.scatter(cluster_data_tracks[:, 0], cluster_data_tracks[:, 1], c=colors[cluster], marker='x')  # Plot tracks data with 'x'

    # Plot the centroids
    plt.scatter(centroids[:, 0], centroids[:, 1], c='black', marker='o', s=100, label="Centroid")

    # Add labels
    #for i, track_name in enumerate(df_spotify['name']):
    #    plt.annotate(track_name, (embedding_spotify[i, 0], embedding_spotify[i, 1]))

    # Add axis labels
    plt.xlabel('t-SNE dimension 1')
    plt.ylabel('t-SNE dimension 2')

    # Add title and description
    plt.title('t-SNE plot of track similarity with KMeans Clusters')
    plt.figtext(0.5, 0.01, "This plot visualizes the similarity between different Spotify tracks based on their audio features. Each point represents a track, and tracks that are closer together in the plot are more similar in terms of their audio features. The plot uses t-SNE (t-Distributed Stochastic Neighbor Embedding), a machine learning algorithm for visualization, to reduce the dimensionality of the data to two dimensions. The colors represent different clusters of tracks created using KMeans clustering.", wrap=True, horizontalalignment='center', fontsize=10)

    # Find the closest song in random_Tracks to each centroid
    closest_songs_random = []
    closest_artists_random = []
    for i, centroid in enumerate(centroids):
        distances = distance.cdist([centroid], embedding_tracks, 'euclidean')[0]
        closest_song_index = np.argmin(distances)
        closest_song = df_tracks.iloc[closest_song_index]
        closest_songs_random.append(closest_song['name'])
        closest_artists_random.append(closest_song['artists'])

    # Return the plot and the closest songs and artists
    return plt, closest_songs_random, closest_artists_random

if __name__ == "__main__":
    plt, closest_songs, closest_artists = run_music_cluster_analysis()
    plt.show()

    print("Recommended songs from random_Tracks (closest to each centroid):")
    for i, (song, artist) in enumerate(zip(closest_songs, closest_artists)):
        print(f"Cluster {i}: {song} by {artist}")