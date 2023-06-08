import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def run_kmeans_clustering():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('spotify.db')

    # Check if the 'top_Tracks' table exists
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='top_Tracks'")
    table_exists = cursor.fetchone() is not None

    if table_exists:
        # Load the existing 'top_Tracks' table into a pandas dataframe
        top_tracks_df = pd.read_sql_query("SELECT * FROM top_Tracks", conn)
    else:
        # Create an empty dataframe if the 'top_Tracks' table does not exist
        top_tracks_df = pd.DataFrame()

    # List of the features to consider for clustering
    features = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness',
                'loudness', 'speechiness', 'tempo', 'valence', 'mode', 'key', 'time_signature']

    if len(top_tracks_df) == 0 or set(features).issubset(top_tracks_df.columns):
        
        # Normalize the features using StandardScaler
        scaler = StandardScaler()
        top_tracks_df[features] = scaler.fit_transform(top_tracks_df[features])

        # Create a KMeans object with a specified number of clusters
        n_clusters = 4
        kmeans = KMeans(n_clusters=n_clusters)

        # Fit the KMeans object to the data and predict the cluster labels
        top_tracks_df['cluster'] = kmeans.fit_predict(top_tracks_df[features])

        # Get the centroids of each cluster
        centroids = kmeans.cluster_centers_

        # Calculate overall mean of each feature
        overall_mean = top_tracks_df[features].mean(axis=0)

        # Get the defining characteristics of each cluster
        defining_characteristics = []
        for i in range(n_clusters):
            # Calculate distance of centroid to overall mean
            distance_to_mean = np.abs(centroids[i] - overall_mean)
            defining_feature_indices = distance_to_mean.argsort()[-3:][::-1]
            defining_features = [features[index]
                                 for index in defining_feature_indices]
            defining_characteristics.append(defining_features)

        # Write the dataframe back to the SQLite database
        top_tracks_df.to_sql('top_Tracks', conn,
                             if_exists='replace', index=False)
    else:
        
        st.warning(
            "The 'top_Tracks' table exists and does not contain the required features. Skipping KMeans clustering.")

        # Set the variables to None
        kmeans = None
        centroids = None
        defining_characteristics = None

    # Close the connection
    conn.close()

    return top_tracks_df, kmeans, features, centroids, defining_characteristics


if __name__ == '__main__':
    run_kmeans_clustering()
