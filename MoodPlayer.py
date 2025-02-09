import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import FastAPI, Query
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import requests

# ✅ Load environment variables
load_dotenv()

# ✅ Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# ✅ Initialize Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mood-to-Playlist Search Mapping
MOOD_PLAYLIST_KEYWORDS = {
    "happy": ["happy vibes", "feel good hits", "sunny day"],
    "sad": ["sad songs", "heartbreak", "melancholy"],
    "chill": ["lofi chill", "relaxing beats", "chill lounge", "study beats"],
    "party": ["party anthems", "club bangers", "night out"],
    "romantic": ["love songs", "date night", "romantic ballads", "slow jams"],
    "focus": ["study focus", "deep work", "instrumental chill", "coding music"],
    "workout": ["gym motivation", "beast mode", "pump up"],
    "sleep": ["sleep relaxation", "deep sleep", "ambient dreams"],
    "roadtrip": ["road trip songs", "driving vibes", "summer drive"],
}

# ✅ Function to Fetch Track Data from Spotify
def get_spotify_track(title, artist):
    query = f"track:{title} artist:{artist}"
    search_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    
    access_token = sp.auth_manager.get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        tracks = results.get("tracks", {}).get("items", [])
        if tracks:
            track = tracks[0]
            return {
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "spotify_url": track["external_urls"]["spotify"],
                "album_cover": track["album"]["images"][0]["url"] if track["album"]["images"] else "https://via.placeholder.com/150"
            }
    return None

# ✅ Fallback Songs with Automatic Data Fetching
FALLBACK_SONGS = {
    "happy": [
        {"title": "Can't Stop the Feeling!", "artist": "Justin Timberlake"},
        {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars"},
    ],
    "sad": [
        {"title": "Someone Like You", "artist": "Adele"},
        {"title": "All I Want", "artist": "Kodaline"},
    ],
    "chill": [
        {"title": "Weightless", "artist": "Marconi Union"},
        {"title": "Cold Little Heart", "artist": "Michael Kiwanuka"},
    ],
    "party": [
        {"title": "Party Rock Anthem", "artist": "LMFAO"},
        {"title": "Turn Down for What", "artist": "DJ Snake, Lil Jon"},
    ],
    "romantic": [
        {"title": "Perfect", "artist": "Ed Sheeran"},
        {"title": "Thinking Out Loud", "artist": "Ed Sheeran"},
    ],
    "focus": [
        {"title": "Weightless", "artist": "Marconi Union"},
        {"title": "Clair de Lune", "artist": "Claude Debussy"},
    ],
    "workout": [
        {"title": "Stronger", "artist": "Kanye West"},
        {"title": "Lose Yourself", "artist": "Eminem"},
    ],
    "sleep": [
        {"title": "Nocturne No. 2", "artist": "Frédéric Chopin"},
        {"title": "Gymnopédie No.1", "artist": "Erik Satie"},
    ],
    "roadtrip": [
        {"title": "Life is a Highway", "artist": "Rascal Flatts"},
        {"title": "Take Me Home, Country Roads", "artist": "John Denver"},
    ],
}

# ✅ Fetch Spotify Track Data for Fallback Songs
for mood, songs in FALLBACK_SONGS.items():
    for i, song in enumerate(songs):
        track_data = get_spotify_track(song["title"], song["artist"])
        if track_data:
            FALLBACK_SONGS[mood][i] = track_data

@app.get("/chat")
def chat(
    mood: str = Query(..., description="Enter your mood (e.g., happy, sad, chill)"),
    refresh: bool = Query(False, description="Set to True to fetch new songs")
):
    mood_lower = mood.lower()
    search_queries = MOOD_PLAYLIST_KEYWORDS.get(mood_lower, ["top hits"])  

    try:
        for query in search_queries:
            playlist_results = sp.search(q=query, type="playlist", limit=5)

            if not playlist_results or not playlist_results.get("playlists") or not playlist_results["playlists"].get("items"):
                continue  

            playlists = playlist_results["playlists"]["items"]
            playlist = random.choice(playlists) if refresh else playlists[0]
            playlist_id = playlist.get("id")

            if not playlist_id:
                continue  

            track_results = sp.playlist_tracks(playlist_id, limit=5)

            if not track_results or not track_results.get("items"):
                continue  

            tracks = [
                {
                    "title": track["track"]["name"],
                    "artist": track["track"]["artists"][0]["name"],
                    "spotify_url": track["track"]["external_urls"]["spotify"],
                    "album_cover": track["track"]["album"]["images"][0]["url"]
                }
                for track in track_results["items"] if track.get("track")
            ]

            if tracks:
                return {"message": f"🎵 Here are some trending {mood_lower} songs:", "mood": mood, "playlist": tracks}

    except:
        pass  # ✅ No error message displayed, just return fallback songs.

    return {"message": f"🎵 Here are some fallback {mood_lower} songs:", "mood": mood, "playlist": FALLBACK_SONGS.get(mood_lower, FALLBACK_SONGS["happy"])}
