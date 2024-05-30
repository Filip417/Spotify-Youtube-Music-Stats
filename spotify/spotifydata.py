import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

CLIENT_ID = "2e20eaf634904ce1907fbd565ceb052e"
CLIENT_SECRET = "21e0ba3a80da4674b53bdd154a193c53"
USERNAME = "314pket55ny6kr5c34lvegl3l3gq"
REDIRECT_URI ="http://example.com"
SCOPE = "user-read-private user-read-email user-read-recently-played user-top-read user-follow-read user-follow-modify playlist-read-private playlist-read-collaborative playlist-modify-public"


token_dict_example = {
'access_token':
'BQCb-NhhYOqSWS-7R8iZlx9oRS6oXVC0QFbms8FmnXT68AVm0Ya3bueXwsP67AE-WlorrDaxZbv1gCW21x1sdyeSRZz1Z4K_vrHycYogFAntMFvn6Y6eCrlU8VoWcdZLD2X2EBjPJHOMXpnZXpIzzo9B1TGPRSpG06sKPia1Vs3cmnoMvoox2Zn7UIE4Z5MyFub1q33-xTOJUY_Xmrhlnr4DjASY6AUuexvLcItIh_FTcN3RZPjmsDY79Ef95-YpJ427ja8oMOeZKKRT',
'refresh_token':
'AQDvkopDzHRqQ-Vqxb1ucNDLjePnKFKE2bp3FYQdcLk-EcEoIg0DVdER3FAofKci4W60RTzbFwl6sLeCpirs85f--0Hy_hFk0ObpXaJaMClGtqNdWV6NgC8KsyLGU9DhD5s'
}

#login for testing, later on through logged user
USERNAME = ''
PASSWORD = ''

#Spotify API info
def create_new_playlist(name, description):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))
    response = sp.user_playlist_create(user=USERNAME,
        name=name,
        public=False,
        description=description)
    print("Playlist has been created.")
    return response["id"]
    
def add_songs_to_playlist(songs,playlist_id):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))
    songs_ids = []
    for song in songs:
        song = sp.search(q=song,limit=1)
        songs_ids.append(song["tracks"]["items"][0]["id"])
    
    sp.user_playlist_add_tracks(user=USERNAME,playlist_id=playlist_id,tracks=songs_ids)
    print("Songs have been added.")

def generate_random_string(length):
    text = ''
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(length):
        text += random.choice(possible)
    return text


def login_to_spotify():
    state_key = generate_random_string(16)
    params = {
        'response_type':'code',
        'client_id':CLIENT_ID,
        'scope':SCOPE,
        'redirect_uri':REDIRECT_URI,
        'state':state_key
    }
    response = requests.get(url='https://accounts.spotify.com/authorize', params=params)
    if response.status_code == 200:
        print(f'Logged into the spotify account sucessfully. Response code: {response.status_code}')
        return state_key
    else:
        error = f'Cannot log into the spotify account. Response code: {response.status_code}'
        print(error)
        return error

def get_access_token_and_refresh_token(state_key):
    if state_key:
        headers = {
            'Authorization': f'Basic {CLIENT_ID}:{CLIENT_SECRET}'
        }
        params = {
            'code': 200,
            'redirect_uri':REDIRECT_URI,
            'grant_type':'authorization_code'
        }
        json = True
        response = requests.post(url='https://accounts.spotify.com/api/token',headers=headers, params=params, json=json)
        print(response)



state_key = login_to_spotify()
get_access_token_and_refresh_token(state_key)