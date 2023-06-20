import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()
client_id = str(os.getenv('CLIENT_ID'))
client_secret = str(os.getenv('CLIENT_SECRET'))

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

token = client_credentials_manager.get_access_token()
print(token)
