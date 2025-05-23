import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REDIRECT_URI = "https://example.com"
SCOPE = os.environ['SCOPE']
USER_ID = os.environ['USER_ID']

date_requested = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
headers = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605."}
URL = f"https://www.billboard.com/charts/hot-100/{date_requested}/"
web_page = requests.get(URL, headers=headers).text
soup = BeautifulSoup(web_page, "html.parser")
song_tags = soup.select("li.o-chart-results-list__item h3.c-title")
song_titles = [song.get_text().strip() for song in song_tags]
year = date_requested.split("-")[0]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))
user = sp.current_user()
track_uris = []
for title in song_titles:
    try:
        result = sp.search(q=f"track:{title} year:{year}", type='track', limit=1)
        tracks = result['tracks']['items']
        if tracks:
            uri = tracks[0]['uri']
            track_uris.append(uri)
            print(f"✅ Found: {title} → {uri}")
        else:
            print(f"❌ Not found on Spotify: {title}")
    except Exception as e:
        print(f"⚠️ Error searching for '{title}': {e}")

playlist_name = f"{date_requested} Billboard 100"
playlist = sp.user_playlist_create(
    user=USER_ID,
    name=playlist_name,
    public=True,  # ✅ Private playlist
    description=f"Top 100 Billboard songs on {date_requested}"
)
print(f"✅ Playlist created: {playlist['name']}")
print(f"🎵 Playlist URL: {playlist['external_urls']['spotify']}")

playlist_id = playlist["id"]

if track_uris:
    sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)
    print(f"✅ {len(track_uris)} songs added to your playlist!")
else:
    print("⚠️ No tracks to add.")
