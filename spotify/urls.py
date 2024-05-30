from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("",views.profile,name="spotify_profile"),
    path("",views.profile,name="spotify"),
    path("download_image/",views.download_image,name='spotify_download_image'),
    path("tracks",views.top_tracks,name="spotify_top_tracks"),
    path("tracks/<str:id>",views.track_detail,name="spotify_track_detail"),
    path("artists",views.top_artists,name="spotify_top_artists"),
    path("artists/<str:id>",views.artist_detail,name="spotify_artist_detail"),
    path("playlists",views.playlists,name="spotify_playlists"),
    path("playlists/<str:id>",views.playlist_detail,name="spotify_playlist_detail"),
    path("albums/<str:id>",views.album_detail,name='spotify_album_detail'),
    path("logout",views.logout,name="spotify_logout")
]
