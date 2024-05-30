from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("",views.profile, name="ytmusic_profile"),
    path("",views.profile, name="ytmusic"),
    path("authorize",views.authorize,name="authorize"),
    path("authorize",views.authorize,name="ytmusic_authorize"),
    path("download_image/",views.download_image,name='ytmusic_download_image'),
    path("tracks",views.top_tracks,name="ytmusic_top_tracks"),
    path("tracks/<str:id>",views.track_detail,name="ytmusic_track_detail"),
    path("artists",views.top_artists,name="ytmusic_top_artists"),
    path("artists/<str:id>",views.artist_detail,name="ytmusic_artist_detail"),
    path("playlists",views.playlists,name="ytmusic_playlists"),
    path("playlists/<str:id>",views.playlist_detail,name="ytmusic_playlist_detail"),
    path("albums/<str:id>",views.album_detail,name='ytmusic_album_detail'),
    path("logout",views.logout,name="ytmusic_logout")
]
