import streamlit as st
import pandas as pd
import sqlite3
from spotifind import personal_spotify_track_collection
from spotifind.top_cluster_analysis import run_top_cluster_analysis
from spotifind import kmeans_clustering
from spotifind.random_cluster_analysis import run_music_cluster_analysis


def main():
    st.set_page_config(page_title="SpotiFind", page_icon="🎵",
                       layout="wide", initial_sidebar_state="expanded")

    st.markdown("<h1 style='text-align: center;'>🎵 Welcome to SpotiFind 🎵</h1>",
                unsafe_allow_html=True)
    st.markdown("# Discover your next favorite song with the power of data! 🚀")

    st.markdown("""
    ### SpotiFind uses the power of K-Means Clustering and your Spotify listening history to suggest new music you'll love. 
    Here's a step by step guide of how SpotiFind works:
    1. **Collect your personal Spotify data**: With your consent, we gather data about your favorite tracks from your Spotify account.
    2. **Show Random Tracks**: You can view a list of randomly selected tracks from our database.
    3. **Kmeans Clustering**: We cluster the songs based on their audio features. This means, songs with similar features get grouped together.
    4. **Plot Centroids and Clustered Data**: We visualize the clusters to help you understand the grouping.
    5. **Get Song Recommendations**: Finally, we recommend songs from the cluster that your favorite tracks belong to.
    """)

    st.sidebar.header("Control Panel")
    collect_data = st.sidebar.button("1. Collect your personal Spotify data")
    show_random_tracks = st.sidebar.button("2. Show Random Tracks")
    kmeans_clustering_button = st.sidebar.button("3. Run Kmeans Clustering")
    plot_data = st.sidebar.button("4. Plot Centroids and Clustered Data")
    get_recommendations_button = st.sidebar.button(
        "5. Get Song Recommendations")
    close_db = st.sidebar.button("Close Database")

    if close_db:
        with st.spinner('Closing the database...'):
            try:
                conn = sqlite3.connect('db/spotify.db')
                conn.close()
                st.success("Database closed successfully.")
            except FileNotFoundError:
                st.error("Database not found.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    if collect_data:
        with st.spinner('Running personal_spotify_track_collection.py...'):
            if "spotify_token_info" in st.session_state:
                personal_spotify_track_collection.run_with_token(
                    st.session_state["spotify_token_info"])
                st.success(
                    "Finished running the personal_spotify_track_collection.py script")

        conn = sqlite3.connect('db/spotify.db')
        top_tracks_df = pd.read_sql_query("SELECT * from top_Tracks", conn)
        st.dataframe(top_tracks_df)

    if kmeans_clustering_button:
        with st.spinner('Running kmeans_clustering.py...'):
            top_tracks_df, kmeans, features, centroids, defining_characteristics = kmeans_clustering.run_kmeans_clustering()

        st.success("KMeans clustering results:")
        st.dataframe(top_tracks_df)

        st.markdown("## Defining Characteristics of Clusters:")
        for i, defining_characteristic in enumerate(defining_characteristics):
            st.markdown(f"**Cluster {i}:** {defining_characteristic}")

        st.success("Finished running the kmeans_clustering.py script")

    if plot_data:
        with st.spinner('Running Music Cluster Analysis...'):
            plot = run_top_cluster_analysis()
        st.pyplot(plot)
        st.success("Finished running Music Cluster Analysis")

    if get_recommendations_button:
        with st.spinner('Getting song recommendations...'):
            plot, closest_songs, closest_artists = run_music_cluster_analysis()
            st.success(
                "Recommended songs from random_Tracks (closest to each centroid):")
            for i, (song, artist) in enumerate(zip(closest_songs, closest_artists)):
                st.markdown(f"**Cluster {i}:** {song} by {artist}")
            st.pyplot(plot)

    if show_random_tracks:
        with st.spinner('Showing random tracks...'):
            conn = sqlite3.connect('db/tracks.db')
            random_tracks_df = pd.read_sql_query(
                "SELECT * from random_Tracks", conn)
            st.dataframe(random_tracks_df)
            conn.close()

    st.markdown("---")
    st.markdown("## About 🎵SpotiFind🎵")
    st.markdown("""
    SpotiFind is a project that aims to help Spotify users discover new music. 
    It uses machine learning algorithms to analyze your favorite tracks and suggest new songs that you might like.
    The project is open-source and you can find the code on [GitHub](https://github.com/yourgithubusername/SpotiFind).
    """)

    st.markdown("## Contact Me")
    st.markdown("""
    If you have any questions, feedback, or suggestions, feel free to reach out to us!
    - Email: JaydinFreemanWork@gmail.com
    - LinkedIn: [Here](https://www.linkedin.com/in/jaydin-freeman/)
    - GitHub: [Here](https://github.com/TheManWhoLikesToCode)
    """)


if __name__ == "__main__":
    main()
