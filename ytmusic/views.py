from django.shortcuts import render, redirect, HttpResponse
import ytmusicapi, os, time, subprocess, platform
from . import image_creator
from io import BytesIO

# For more details please see the ytmusicapi docs: https://ytmusicapi.readthedocs.io/en/stable/
# Used for validation and getting ytmusic instance
def get_ytmusic_instance(request):
    if not request.session.get('authenticated'):
        return redirect('authorize')
    
    cookie_value = request.session.get('cookie')
    if not cookie_value:
        return redirect('authorize')

    headers_raw = HEADERS_RAW.replace('[cookie_user_input]', cookie_value)
    try:
        YTinput = ytmusicapi.setup(headers_raw=headers_raw)
        ytmusic = ytmusicapi.YTMusic(YTinput)
        return ytmusic
    except:
        print('Cookie value is invalid')
        return redirect('authorize')

# Create your views here.
def profile(request):
    LIMIT = 5

    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        try:
            profile = ytmusic.get_account_info()
            top_tracks = ytmusic.get_liked_songs(LIMIT)
            top_artists = ytmusic.get_library_artists(LIMIT)
            top_artist = ytmusic.get_artist(top_artists[0]['browseId'])
        except:
            return redirect('authorize')

        if not profile:
            return redirect('authorize')

        context = {
            'profile': profile,
            'top_tracks':top_tracks['tracks'][:5],
            'top_artists':top_artists[:5],
            'top_artist':top_artist,
        }
        return render(request, 'ytmusic/profile.html', context)


def authorize(request):
    if request.method == 'POST':
        cookie_value = request.POST.get('cookie', '')
        request.session['cookie'] = cookie_value
        request.session['authenticated'] = True
        request.session.modified = True
        return redirect('profile')
    return render(request, 'ytmusic/authorize.html')


def top_tracks(request):
    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        if request.method == 'POST':
            term = request.POST.get('term', None)
            if term == 'recent':
                top_tracks = ytmusic.get_history()
                today = time.strftime("%d %m %Y")
                video_ids_of_top_tracks = [track['videoId'] for track in top_tracks]
                playlist = ytmusic.create_playlist(title='My recently played songs',
                                        description=f'created on {today}',
                                        privacy_status='PUBLIC',
                                        video_ids=video_ids_of_top_tracks,
                                        )
                context = {
                        'top_tracks':top_tracks,
                        'term':term,
                        'playlist':playlist,
                        }
                return render(request, "ytmusic/tracks.html", context)
            if term == 'liked':
                top_tracks = ytmusic.get_liked_songs()
                top_tracks = top_tracks['tracks']
                today = time.strftime("%d %m %Y")
                video_ids_of_top_tracks = [track['videoId'] for track in top_tracks]
                playlist = ytmusic.create_playlist(title='My liked songs',
                                        description=f'created on {today}',
                                        privacy_status='PUBLIC',
                                        video_ids=video_ids_of_top_tracks,
                                        )
                context = {
                        'top_tracks':top_tracks,
                        'term':term,
                        'playlist':playlist,
                        }
                return render(request, "ytmusic/tracks.html", context)           

        if request.method == 'GET':
            term = request.GET.get('term','liked')
            if term == 'liked':
                top_tracks = ytmusic.get_liked_songs()
                top_tracks = top_tracks['tracks']
            elif term == 'recent':
                top_tracks = ytmusic.get_history()

            context = {
                    'top_tracks':top_tracks,
                    'term':term,
                    }
            return render(request, "ytmusic/tracks.html", context)

        try:
            top_tracks = ytmusic.get_liked_songs()
        except:
            return redirect('/')
        
        context = {
            'top_tracks':top_tracks['tracks'],
            'term':'liked'
        }
        return render(request, 'ytmusic/tracks.html', context)

def top_artists(request):
    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        try:
            top_artists = ytmusic.get_library_artists()
        except:
            return redirect('/')
        context = {
            'top_artists':top_artists
        }
        return render(request, "ytmusic/artists.html", context)

def track_detail(request, id):
    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        try:
            track = ytmusic.get_song(id)
        except:
            return redirect('/')
        context = {
            'track':track
        }
        return render(request, "ytmusic/track.html", context)

def artist_detail(request, id):
    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        try:
            artist = ytmusic.get_artist(id)
        except:
            return redirect('/')
        context = {
            'artist':artist
        }
        return render(request, "ytmusic/artist.html", context)

def album_detail(request, id):
    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        try:
            album = ytmusic.get_album(id)
        except:
            return redirect('/')
        context = {
            'album':album
        }
        return render(request, "ytmusic/album.html", context)

def playlists(request):
    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        try:
            playlists = ytmusic.get_library_playlists()
        except:
            return redirect('/')
        context = {
            'playlists':playlists
        }
        return render(request, "ytmusic/playlists.html", context)

def playlist_detail(request, id):
    ytmusic = get_ytmusic_instance(request)
    if not isinstance(ytmusic, ytmusicapi.YTMusic):
        return ytmusic
    else:
        try:
            playlist = ytmusic.get_playlist(id)
        except:
            return redirect('/')
        context = {
            'playlist':playlist
        }
        return render(request, "ytmusic/playlist.html", context)

def download_image(request):
    if request.method == 'POST':
        # Retrieve term from the POST data, defaulting to 'long_term' if not present
        name = request.POST.get('name',None)
        top_artists = request.POST.get('top_artists', None)
        top_tracks = request.POST.get('top_tracks', None)
        top_artist = request.POST.get('top_artist', None)
        
        # Assuming image_creator.get_image() returns a PIL image object
        image_data = image_creator.get_image(name, top_artists=top_artists, top_tracks=top_tracks, top_artist=top_artist)

        # Create a BytesIO object to hold the image data
        image_io = BytesIO()
        # Save the PIL image to the BytesIO object as PNG
        image_data.save(image_io, format='PNG')
        # Move to the beginning of the BytesIO buffer
        image_io.seek(0)

        # Set up the HTTP response
        response = HttpResponse(image_io, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{name} YT Music Summary.png"'
        response['Content-Transfer-Encoding'] = 'binary'
        return response
    else:
        # Handle requests that are not POST
        return HttpResponse("Method not allowed", status=405)
    
def logout(request):
    request.session['cookie'] = ''
    request.session['authenticated'] = False
    request.session.modified = True
    return redirect('/')


# Headers raw to authenticate ytmusicapi without using terminal
# More details please see the ytmusic docs: https://ytmusicapi.readthedocs.io/en/stable/
HEADERS_RAW = """Alt-Svc:
h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
Cache-Control:
private
Content-Encoding:
br
Content-Length:
15602
Content-Type:
application/json; charset=UTF-8
Date:
Sun, 26 May 2024 13:39:16 GMT
Expires:
Sun, 26 May 2024 13:39:16 GMT
Server:
scaffolding on HTTPServer2
Set-Cookie:
SIDCC=AKEyXzUlzY_M9bChIGWAP5e9i0o59rmNnglXQiH0mcJ4HXBeBUwQL8dMObZuW04VdsPqBvn7J0A; expires=Mon, 26-May-2025 13:39:16 GMT; path=/; domain=.youtube.com; priority=high
Set-Cookie:
__Secure-1PSIDCC=AKEyXzUy06gvtKXE0Zp-Xojl_FnzaOrCNK-TLoljWjYInM_6r1xBmZyIAnelDDR3UES6_mt5uRA8; expires=Mon, 26-May-2025 13:39:16 GMT; path=/; domain=.youtube.com; Secure; HttpOnly; priority=high
Set-Cookie:
__Secure-3PSIDCC=AKEyXzUV8GAg215Oc19zID3FYODILW8txhSVY4zI8FrCQ5Epc2-6CbrUUvip_d9knLdc8Fn0gEnF; expires=Mon, 26-May-2025 13:39:16 GMT; path=/; domain=.youtube.com; Secure; HttpOnly; priority=high; SameSite=none
Vary:
Origin
Vary:
X-Origin
Vary:
Referer
X-Content-Type-Options:
nosniff
X-Frame-Options:
SAMEORIGIN
X-Xss-Protection:
0
:authority:
music.youtube.com
:method:
POST
:path:
/youtubei/v1/browse?ctoken=4qmFsgKhAhIMRkVtdXNpY19ob21lGpACQ0FONnh3RkhTVlJ5YW1KbE5IRTBXVVJYYjBWQ1EyNDRTMHBJYkRCWU0wSm9XakpXWm1NeU5XaGpTRTV2WWpOU1ptSllWbnBoVjA1bVkwZEdibHBXT1hsYVYyUndZakkxYUdKQ1NXWmhNMnhKWWxkUmVWUkhOWFpWYlU1b1ZsVk5ORmw2VVhSalYzUnJZVlpCTUdSc1JtdFZlVEUwV25odk1sUllWbnBoVjA1RllWaE9hbUl6V214amJteFJXVmRrYkZVeVZubGtiV3hxV2xNeFNGcFlVa2xpTWpGc1ZVZEdibHBSUVVKQlNFSnpRVUZHU0ZGblFVSlNNRWxCUVZGRlJDMXdla2gyVVd0RFEwRlI%253D&continuation=4qmFsgKhAhIMRkVtdXNpY19ob21lGpACQ0FONnh3RkhTVlJ5YW1KbE5IRTBXVVJYYjBWQ1EyNDRTMHBJYkRCWU0wSm9XakpXWm1NeU5XaGpTRTV2WWpOU1ptSllWbnBoVjA1bVkwZEdibHBXT1hsYVYyUndZakkxYUdKQ1NXWmhNMnhKWWxkUmVWUkhOWFpWYlU1b1ZsVk5ORmw2VVhSalYzUnJZVlpCTUdSc1JtdFZlVEUwV25odk1sUllWbnBoVjA1RllWaE9hbUl6V214amJteFJXVmRrYkZVeVZubGtiV3hxV2xNeFNGcFlVa2xpTWpGc1ZVZEdibHBSUVVKQlNFSnpRVUZHU0ZGblFVSlNNRWxCUVZGRlJDMXdla2gyVVd0RFEwRlI%253D&type=next&itct=CBAQybcCIhMI3YDqtrirhgMVaMVJBx0amgc1&prettyPrint=false
:scheme:
https
Accept:
*/*
Accept-Encoding:
gzip, deflate, br, zstd
Accept-Language:
en,en-US;q=0.9,pl;q=0.8
Authorization:
SAPISIDHASH 1716730755_4211409fc1adf5c31d24171e77ddc36db2dae225
Content-Length:
2636
Content-Type:
application/json
Cookie:
[cookie_user_input]
Origin:
https://music.youtube.com
Priority:
u=1, i
Referer:
https://music.youtube.com/
Sec-Ch-Ua:
"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"
Sec-Ch-Ua-Arch:
"x86"
Sec-Ch-Ua-Bitness:
"64"
Sec-Ch-Ua-Full-Version:
"125.0.6422.112"
Sec-Ch-Ua-Full-Version-List:
"Google Chrome";v="125.0.6422.112", "Chromium";v="125.0.6422.112", "Not.A/Brand";v="24.0.0.0"
Sec-Ch-Ua-Mobile:
?0
Sec-Ch-Ua-Model:
""
Sec-Ch-Ua-Platform:
"Windows"
Sec-Ch-Ua-Platform-Version:
"15.0.0"
Sec-Ch-Ua-Wow64:
?0
Sec-Fetch-Dest:
empty
Sec-Fetch-Mode:
same-origin
Sec-Fetch-Site:
same-origin
User-Agent:
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36
X-Client-Data:
CIa2yQEIo7bJAQipncoBCMWQywEIk6HLAQjdmM0BCIWgzQEIkofOAQjik84BCOiTzgE=
Decoded:
message ClientVariations {
  // Active client experiment variation IDs.
  repeated int32 variation_id = [3300102, 3300131, 3313321, 3328069, 3330195, 3361885, 3362821, 3376018, 3377634, 3377640];
}
X-Goog-Authuser:
0
X-Goog-Visitor-Id:
CgsyNnJXdnVoa2JNZyiD98yyBjIKCgJHQhIEGgAgIA%3D%3D
X-Origin:
https://music.youtube.com
X-Youtube-Bootstrap-Logged-In:
true
X-Youtube-Client-Name:
67
X-Youtube-Client-Version:
1.20240522.01.00
Error causes in the Console
The Console now shows you chains of error causes in the stack trace.
CSS selector statistics in Performance
The Performance panel can now show you CSS selector statistics for long-running Recalculate Style events.
Early Hints headers in Network
The Network panel now lets you inspect and debug Early Hints headers."""
