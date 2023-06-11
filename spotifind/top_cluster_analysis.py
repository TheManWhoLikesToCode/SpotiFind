import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

def run_top_cluster_analysis():
    # Connect to the SQLite database
    conn = sqlite3.connect("db/spotify.db")

    # Load the data into a pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM top_Tracks", conn)

    # Close the connection
    conn.close()

    # Extract the features from the DataFrame
    features = df.drop(['id', 'name', 'artists'], axis=1)

    # Normalize the features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Compute the t-SNE embedding
    tsne = TSNE(n_components=2, random_state=0, init='random', learning_rate=200)
    embedding = tsne.fit_transform(features_scaled)

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=5, random_state=0).fit(embedding)

    # Assign each data point to a cluster
    df['cluster'] = kmeans.labels_

    # Extract the centroids
    centroids = kmeans.cluster_centers_

    # Create a color map for the clusters
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # Plot the t-SNE embedding with clusters
    plt.figure(figsize=(10, 10))

    for cluster in range(5):
        cluster_data = embedding[df['cluster'] == cluster]
        plt.scatter(cluster_data[:, 0], cluster_data[:, 1], c=colors[cluster], label=f"Cluster {cluster}")

    # Plot the centroids
    plt.scatter(centroids[:, 0], centroids[:, 1], c='black', marker='x', s=100, label="Centroid")

    # Add labels
    #for i, track_name in enumerate(df['name']):
    #    plt.annotate(track_name, (embedding[i, 0], embedding[i, 1]))

    # Add axis labels
    plt.xlabel('t-SNE dimension 1')
    plt.ylabel('t-SNE dimension 2')

    # Add title and description
    plt.title('t-SNE plot of track similarity with KMeans Clusters')
    plt.figtext(0.5, 0.01, "This plot visualizes the similarity between different Spotify tracks based on their audio features. Each point represents a track, and tracks that are closer together in the plot are more similar in terms of their audio features. The plot uses t-SNE (t-Distributed Stochastic Neighbor Embedding), a machine learning algorithm for visualization, to reduce the dimensionality of the data to two dimensions. The colors represent different clusters of tracks created using KMeans clustering.", wrap=True, horizontalalignment='center', fontsize=10)

    # Add legend
    plt.legend(loc="upper right")

    # Return the plot
    return plt


