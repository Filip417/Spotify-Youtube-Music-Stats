# Spotify Youtube Music Stats

A web app for visualizing personalized Spotify and YouTube Music statistics and generating up-to-date live "Spotify Wrapped" images.

[APP](https://spotify-youtube-music-stats-6cec4f95b0e4.herokuapp.com/)

## Table of Contents

- [Example of 'Spotify Wrapped' Feature](#example-of-spotify-wrapped-feature)
- [Demo Video](#demo-video)
- [Features](#features)
- [Data Available](#data-available)
- [Credit](#credit)
- [Requirements](#requirements)
- [Installation and Deployment](#installation-and-deployment)
- [Contributing](#contributing)
- [License](#license)

## Example of 'Spotify Wrapped' Feature

<img src="https://raw.githubusercontent.com/Filip417/Spotify-Youtube-Music-Stats/main/readmeimages/spotify%20wrapped%20example.png" alt="Example of 'Spotify Wrapped' Feature Image" width="270" height="480"/>

## Demo Video

![Spotify Youtube Music Stats Demo Video GIF](https://raw.githubusercontent.com/Filip417/Spotify-Youtube-Music-Stats/main/readmeimages/Spotify%20YouTube%20Music%20Stats%20gif%20demo.gif)

## Features

This web app visualizes current Spotify and YouTube Music statistics such as user's basic information, top tracks, top artists, and playlists. Additionally, it provides data on individual tracks, artists, playlists, and albums. Additionally:

- Create new playlists with top tracks from a user-defined term.
- Download 'Spotify Wrapped'-like images with current data from the last 4 weeks, 6 months, or a year.

**Note:** The official Spotify Wrapped is released annually, accessible until early January. This 'Spotify Wrapped' feature, while more limited, offers stats anytime and allows for customizable time horizons (monthly, bi-annually, annually).

## Data Available

### User:
- Image
- Username
- Number of followers & following
- Number of playlists

### Track:
- Title
- Artists
- Album
- Duration
- Analysis: Key, Modality, Tempo
- Features: Acousticness, Danceability, Energy, Instrumentalness, Liveness, Speechiness, Valence

### Artist:
- Image
- Name
- Genres
- Popularity (%)
- Number of followers
- List of albums
- List of tracks

### Playlist:
- Image
- Title
- Description
- List of tracks
- Number of followers
- Owner's name

### Album:
- Image
- List of tracks
- Release date
- Popularity (%)

### Spotify Wrapped:
- Top artist image
- Top 5 artists
- Top 5 tracks
- Average popularity of top 5 artists
- Top genre among top 5 artists
- User's username
- Time horizon (Last month, Last 6 months, Last year)

## Credit
Huge thank you and credit to @bchiang7 and all contributors to the original Spotify Profile Web App [Spotify Profile](https://github.com/bchiang7/spotify-profile).

I have recreated the design and features using the Python Django library, adding access to more data, albums, time horizon filters, playlist saving, 'Spotify Wrapped' image generation, and extended the app to YouTube Music with limited data visibility due to the absence of a comprehensive official API like Spotify's.

## Requirement
I deeply appreciate Spotify for providing a well-documented official API that facilitates creating apps with easy authorization methods and a secure system for user information. [Spotify Official API](https://developer.spotify.com/documentation/web-api)


Huge thanks to @sigma67 and all contributors to the unofficial YouTube Music API, which enabled expansion of the app's capabilities to include YouTube Music. [ytmusicapi](https://github.com/sigma67/ytmusicapi)


How to install requirements using python:
```python
pip install -r /path/to/requirements.txt
```

* Required python libraries:
Django==5.0.6
Pillow==10.3.0
Requests==2.32.3
ytmusicapi==1.7.3
python-decouple==3.8
gunicorn==22.0.0
whitenoise==6.0.0
django-compressor==3.0
dj-database-url==2.2.0

## Deploying to Heroku, Installation

Spotify developer api requirement

```python
# Create new heroku app
heroku create app-name

# Set Heroku environment variables
heroku config:set CLIENT_ID=XXXXX -a app-name
heroku config:set REDIRECT_URI=https://app-name.herokuapp.com/spotify -a app-name
heroku config:set DJANGO_SECRET_KEY=your-django-secret-key -a app-name

# Push to Heroku
git push heroku master
```
Add http://app-name.herokuapp.com/spotify as a Redirect URI in the spotify application settings

Once the app is live on Heroku, hitting http://app-name.herokuapp.com/ should be the same as hitting http://127.0.0.1:8000/

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss the changes you propose.

New features, improvement suggestions, or bug reports are highly appreciated.

## License
This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).