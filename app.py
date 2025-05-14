import streamlit as st
import pickle
import pandas as pd
import requests

# TMdb requires VPN to work
api_key = 'API key'  # Replace with your actual API key

# Function to fetch movie details from TMDb
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        overview = data.get('overview', 'No overview available.')
        rating = data.get('vote_average', 'N/A')
        tmdb_url = f"https://www.themoviedb.org/movie/{movie_id}"
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/150?text=No+Image"
        return poster_url, overview, rating, tmdb_url
    except:
        return "https://via.placeholder.com/150?text=No+Image", "No overview available.", "N/A", "#"

# Load data
movie_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_list = movie_df['title'].values

# Recommendation function
def recommend(movie_name):
    movie_name = movie_name.lower()
    titles_lower = movie_df['title'].str.lower()

    if movie_name not in titles_lower.values:
        return []

    movie_index = titles_lower[titles_lower == movie_name].index[0]
    distances = list(enumerate(similarity[movie_index]))
    sorted_distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]

    recommended = []
    for i in sorted_distances:
        movie_id = movie_df.iloc[i[0]].movie_id
        title = movie_df.iloc[i[0]].title
        poster_url, overview, rating, tmdb_url = fetch_movie_details(movie_id)
        recommended.append({
            'title': title,
            'poster': poster_url,
            'overview': overview,
            'rating': rating,
            'url': tmdb_url
        })

    return recommended

# Streamlit UI Enhancements

# Set custom background image
st.markdown("""
    <style>
    body {
        background-image: url('https://your-background-image-link.jpg');  /* Update with a valid background image URL */
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    .stButton>button {
        background-color: #0078D4;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #005F9E;
    }
    .stSelectbox>div>div>div {
        background-color: rgba(0, 0, 0, 0.6) !important;
    }
    .stMarkdown {
        font-family: 'Arial', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title('🎬 Movie Recommender by Ashvin')
st.markdown("Find movies you love! Just select a movie and let us recommend similar ones.")

selected_movie_name = st.selectbox(
    'Type a movie name and let us give you similar movies:',
    movies_list
)

if st.button('Search'):
    recommendations = recommend(selected_movie_name)
    if recommendations:
        for movie in recommendations:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(movie['poster'], width=150)
            with col2:
                st.markdown(f"### [{movie['title']}]({movie['url']})")
                st.markdown(f"**Rating:** {movie['rating']}/10")
                st.markdown(f"**Overview:** {movie['overview']}")
    else:
        st.warning("Movie not found. Please try a different title.")



