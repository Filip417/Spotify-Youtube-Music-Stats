from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
import urllib.parse, hashlib, base64, random, requests, time
from . import image_creator
from io import BytesIO
from decouple import Config

# To adjust the visible terms
TIMES_TRANSLATOR = {
            'long_term': 'Last year',
            'medium_term': 'Last 6 months',
            'short_term': 'Last 4 weeks'
        }

#Default term for top_tracks and top_artists long_term, so approx. last year
DEFAULT_TERM = 'long_term'

# ALL functions to fetch and engage with Spotify API
# Official URL: https://developer.spotify.com/documentation/web-api
# Needs to set up app at https://developer.spotify.com/ to get CLIENT_ID and set REDIRECT_URI


config = Config()
CLIENT_ID = config('CLIENT_ID')
REDIRECT_URI = config('REDIRECT_URI')

def generate_code_verifier(length=128):
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(possible) for _ in range(length))

def generate_code_challenge(code_verifier):
    code_verifier_bytes = code_verifier.encode('utf-8')
    sha256_digest = hashlib.sha256(code_verifier_bytes).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_digest).decode('utf-8').rstrip('=')
    return code_challenge

def redirect_to_auth_code_flow(client_id, request):
    verifier = generate_code_verifier(128)
    challenge = generate_code_challenge(verifier)
    request.session['verifier'] = verifier

    params = {
        'client_id':client_id,
        'response_type':'code',
        'redirect_uri':REDIRECT_URI,
        'scope':'user-read-private user-read-email user-follow-read user-top-read user-library-read playlist-read-private playlist-read-collaborative user-read-recently-played playlist-modify-public playlist-modify-private',
        'code_challenge_method':'S256',
        'code_challenge':challenge
    }
    url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(params)
    return url

def get_access_token(client_id, code, request):
    verifier = request.session.get('verifier')
    headers = {
        'Content-Type':'application/x-www-form-urlencoded'
    }
    data = {
        'client_id':client_id,
        'grant_type':'authorization_code',
        'code':code,
        'redirect_uri':REDIRECT_URI,
        'code_verifier':verifier,
    }
    response = requests.post(url='https://accounts.spotify.com/api/token', headers=headers, data=data)
    response_data = response.json()
    
    if response.status_code != 200:
        raise ValueError(f"Error fetching access token: {response_data}")

    return response_data['access_token']

def get_profile(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url='https://api.spotify.com/v1/me', headers=headers)
    return response.json()

def get_followed(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url='https://api.spotify.com/v1/me/following?type=artist', headers=headers)
    return response.json()

def get_track(access_token, id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url=f'https://api.spotify.com/v1/tracks/{id}', headers=headers)
    return response.json()

def get_track_features(access_token, id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url=f'https://api.spotify.com/v1/audio-features/{id}', headers=headers)
    return response.json()

def get_track_analysis(access_token, id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url=f'https://api.spotify.com/v1/audio-analysis/{id}', headers=headers)
    return response.json()

def get_top_tracks(access_token, limit, time_range = DEFAULT_TERM):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'time_range':time_range,
        'limit':limit
    }
    response = requests.get(url='https://api.spotify.com/v1/me/top/tracks', headers=headers, params=params)
    return response.json()

def get_artist(access_token, id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url=f'https://api.spotify.com/v1/artists/{id}', headers=headers)
    return response.json()

def get_artist_top_tracks(access_token, id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url=f'https://api.spotify.com/v1/artists/{id}/top-tracks', headers=headers)
    return response.json()

def get_artist_albums(access_token, id, limit):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'limit':limit
    }
    response = requests.get(url=f'https://api.spotify.com/v1/artists/{id}/albums', headers=headers, params=params)
    return response.json()

def get_top_artists(access_token, limit, time_range = DEFAULT_TERM):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'time_range':time_range,
        'limit':limit
    }
    response = requests.get(url='https://api.spotify.com/v1/me/top/artists', headers=headers, params=params)
    return response.json()

def get_saved(access_token, limit):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'limit':limit
    }
    response = requests.get(url='https://api.spotify.com/v1/me/tracks', headers=headers, params=params)
    return response.json()

def get_album(access_token, id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url=f'https://api.spotify.com/v1/albums/{id}', headers=headers)
    return response.json()

def create_playlist(access_token, id, name, description):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    body = {
        'name':name,
        'description':description
    }
    response = requests.post(url=f'https://api.spotify.com/v1/users/{id}/playlists/', headers=headers, json=body)
    return response.json()

def add_tracks_to_playlist(access_token, playlist_id, list_of_tracks_uris):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    body = {
        'uris':list_of_tracks_uris
    }
    response = requests.post(url=f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, json=body)
    return response.json()

def get_playlist(access_token, id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url=f'https://api.spotify.com/v1/playlists/{id}', headers=headers)
    return response.json()

def get_playlists(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'limit':50
    }
    response = requests.get(url='https://api.spotify.com/v1/me/playlists', headers=headers, params=params)
    return response.json()

def get_recent(access_token, limit):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'limit':limit
    }
    response = requests.get(url='https://api.spotify.com/v1/me/player/recently-played', headers=headers, params=params)
    return response.json()

# Function that checks Spotify API response
def check_response(response, request):
    try:
        if response['error']:
            request.session['access_token'] = None
            request.session.modified = True
            return redirect('/')
    except KeyError:
        print('Access code is correct.')

# Create your views here.
def profile(request):
    LIMIT = 5
    access_token = request.session.get('access_token', None)
    code = request.GET.get('code', None)
    if not code and not access_token:
        # Starts authentication workflow profided by Spotify API
        url = redirect_to_auth_code_flow(CLIENT_ID, request)
        return redirect(url)
    else:
        if not access_token:
            # Gets access token and saves it in Cookies
            access_token = get_access_token(CLIENT_ID, code, request)
            request.session['access_token'] = access_token
            request.session.modified = True
            print('Executed to get access_token')

        if request.method == 'GET':
            profile = get_profile(access_token)
            result = check_response(profile, request)
            if result:
                return result
            term = request.GET.get('term', DEFAULT_TERM)
            top_tracks = get_top_tracks(access_token, LIMIT, term)
            top_artists = get_top_artists(access_token, LIMIT, term)
            playlists = get_playlists(access_token)
            followed = get_followed(access_token)
            context = {
                'profile':profile,
                'followed':followed,
                'top_tracks':top_tracks,
                'top_artists':top_artists,
                'playlists':playlists,
                'term':term
            }
            return render(request, "spotify/profile.html", context)
        
        profile = get_profile(access_token)
        try:
            if profile['error']:
                request.session['access_token'] = None
                request.session.modified = True
                url = redirect_to_auth_code_flow(CLIENT_ID, request)
                return redirect(url)
        except KeyError:
            print('Access code is correct.')
        try:
            request.session['user_id'] = profile['id']
            request.session.modified = True
        except KeyError:
            print('unable to set user ID')
        followed = get_followed(access_token)
        top_tracks = get_top_tracks(access_token, LIMIT)
        top_artists = get_top_artists(access_token, LIMIT)
        playlists = get_playlists(access_token)
        context = {
            'profile':profile,
            'followed':followed,
            'top_tracks':top_tracks,
            'top_artists':top_artists,
            'playlists':playlists,
            'term':term
            }
    return render(request, "spotify/profile.html", context)

def download_image(request):
    if request.method == 'POST':
        # Retrieve term from the POST data, defaulting if not present
        term = request.POST.get('term', DEFAULT_TERM)
        top_artists = request.POST.get('top_artists',None)
        top_tracks = request.POST.get('top_tracks',None)
        name = request.POST.get('name',None)

        # Translate the term into human-readable format
        
        term_readable = TIMES_TRANSLATOR.get(term, 'Unknown')

        # Assuming image_creator.get_image() returns a PIL image object
        image_data = image_creator.get_image(name, top_artists=top_artists, top_tracks=top_tracks, term_readable=term_readable)

        # Create a BytesIO object to hold the image data
        image_io = BytesIO()
        # Save the PIL image to the BytesIO object as PNG
        image_data.save(image_io, format='PNG')
        # Move to the beginning of the BytesIO buffer
        image_io.seek(0)

        # Set up the HTTP response
        response = HttpResponse(image_io, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{name} Spotify Summary {term_readable}.png"'
        return response
    else:
        # Handle requests that are not POST
        return HttpResponse("Method not allowed", status=405)

def top_tracks(request):
    LIMIT = 50
    access_token = request.session.get('access_token', None)

    if not access_token:
        return redirect('/')
    
    if request.method == 'POST':
        term = request.POST.get('term', None)
        if term == 'saved':
            top_tracks = get_saved(access_token, LIMIT)
        elif term == 'recent':
            top_tracks = get_recent(access_token, LIMIT)
        else:
            top_tracks = get_top_tracks(access_token, LIMIT, term)

        today = time.strftime("%d %m %Y")
        user_id = request.session.get('user_id', None)
        if user_id:
            playlist = create_playlist(access_token, user_id,
                                    'My Top Songs',
                                    f'from {TIMES_TRANSLATOR.get(term, 'Lately')} - created on {today}'
                                    )
            playlist_id = playlist['id']
            tracks_uris = [track['uri'] for track in top_tracks['items']]
            add_tracks_to_playlist(access_token, playlist_id, tracks_uris)
        context = {
            'top_tracks': top_tracks,
            'term': term,
            'playlist':playlist,
            }
        return render(request, "spotify/tracks.html", context)

    if request.method == 'GET':
        term = request.GET.get('term', DEFAULT_TERM)
        if term == 'saved':
            top_tracks = get_saved(access_token, LIMIT)
        elif term == 'recent':
            top_tracks = get_recent(access_token, LIMIT)
        else:
            top_tracks = get_top_tracks(access_token, LIMIT, term)
        context = {
            'top_tracks':top_tracks,
            'term':term,
            }
        return render(request, "spotify/tracks.html", context)
    
    top_tracks = get_top_tracks(access_token, LIMIT)
    result = check_response(top_tracks, request)
    if result:
        return result
    context = {
        'top_tracks':top_tracks,
        'term':term,
        }
    return render(request, "spotify/tracks.html", context)

def top_artists(request):
    LIMIT = 50
    access_token = request.session.get('access_token', None)

    if not access_token:
        return redirect('/')
    
    if request.method == 'GET':
        term = request.GET.get('term', DEFAULT_TERM)
        top_artists = get_top_artists(access_token, LIMIT, term)
        context = {
            'top_artists':top_artists,
            'term':term,
            }
        return render(request, "spotify/artists.html", context)
    
    top_artists = get_top_artists(access_token, LIMIT)
    result = check_response(top_artists, request)
    if result:
        return result
    context = {
        'top_artists':top_artists,
        'term':term,
    }
    return render(request, "spotify/artists.html", context)

def playlists(request):
    access_token = request.session.get('access_token', None)

    if not access_token:
        return redirect('/')
    
    playlists = get_playlists(access_token)
    result = check_response(playlists, request)
    if result:
        return result
    context = {
        'playlists':playlists
    }
    print(f'Last playlist: {playlists['items'][-1]}')
    return render(request, "spotify/playlists.html", context)

# Views for detailed pages
def track_detail(request, id):
    access_token = request.session.get('access_token', None)

    if not access_token:
        return redirect('/')
    
    track = get_track(access_token, id)
    result = check_response(track, request)
    if result:
        return result
    track_features = get_track_features(access_token, id)
    track_analysis = get_track_analysis(access_token, id)
    context = {
        'track':track,
        'track_features':track_features,
        'track_analysis':track_analysis,
    }
    return render(request, "spotify/track.html", context)

def artist_detail(request, id):
    access_token = request.session.get('access_token', None)

    if not access_token:
        return redirect('/')
    
    artist = get_artist(access_token, id)
    result = check_response(artist, request)
    if result:
        return result
    top_tracks = get_artist_top_tracks(access_token, id)
    albums = get_artist_albums(access_token, id, 10)
    context = {
        'artist':artist,
        'top_tracks':top_tracks,
        'albums':albums,
    }
    return render(request, "spotify/artist.html", context)

def playlist_detail(request, id):
    access_token = request.session.get('access_token', None)

    if not access_token:
        return redirect('/')
    
    playlist = get_playlist(access_token, id)
    result = check_response(playlist, request)
    if result:
        return result
    context = {
        'playlist':playlist,
    }
    return render(request, "spotify/playlist.html", context)

def album_detail(request, id):
    access_token = request.session.get('access_token', None)

    if not access_token:
        return redirect('/')
    
    album = get_album(access_token, id)
    result = check_response(album, request)
    if result:
        return result
    context = {
        'album':album,
    }
    return render(request, "spotify/album.html", context)

def logout(request):
    request.session['access_token'] = None
    request.session.modified = True
    return redirect('/')