import logging

from functools import lru_cache
from mopidy.models import Ref, Artist, Album, Track

logger = logging.getLogger(__name__)


def to_artists(tidal_artists):
    return [to_artist(a) for a in tidal_artists]

@lru_cache(maxsize=128)
def to_artist(tidal_artist):
    if tidal_artist is None:
        return None

    return Artist(uri='tidal-moppina:artist:' + str(tidal_artist.id),
                  name=tidal_artist.name)

def to_albums(tidal_albums):
    return [to_album(a, None) for a in tidal_albums]

@lru_cache(maxsize=128)
def to_album(tidal_album, artist):
    if artist is None:
        artist = to_artist(tidal_album.artist)
    return Album(uri='tidal-moppina:album:' + str(tidal_album.id),
                 name=tidal_album.name,
                 artists=[artist])


def to_tracks(tidal_tracks):
    return [to_track(None, None, t) for t in tidal_tracks]

@lru_cache(maxsize=128)
def to_track(artist, album, tidal_track):
    uri = 'tidal-moppina:track:{0}:{1}:{2}'.format(tidal_track.artist.id,
                                           tidal_track.album.id,
                                           tidal_track.id)
    if artist is None:
        artist = to_artist(tidal_track.artist)
    if album is None:
        album = to_album(tidal_track.album, artist)

    track_len = tidal_track.duration * 1000
    return Track(uri=uri,
                 name=tidal_track.name,
                 track_no=tidal_track.track_num,
                 artists=[artist],
                 album=album,
                 length=track_len,
                 disc_no=tidal_track.disc_num)

def to_artists_ref(tidal_artists):
    return [to_artist_ref(a) for a in tidal_artists]

@lru_cache(maxsize=128)
def to_artist_ref(tidal_artist):
    return Ref.artist(uri='tidal-moppina:artist:' + str(tidal_artist.id),
                      name=tidal_artist.name)

def to_playlists_ref(tidal_playlists):
    return [to_playlist_ref(p) for p in tidal_playlists]

@lru_cache(maxsize=128)
def to_playlist_ref(tidal_playlist):
    return Ref.playlist(uri='tidal-moppina:playlist:' + str(tidal_playlist.id),
                        name=tidal_playlist.name)

def to_moods_ref(tidal_moods):
    return [to_mood_ref(m) for m in tidal_moods]

@lru_cache(maxsize=128)
def to_mood_ref(tidal_mood):
    return Ref.playlist(uri='tidal-moppina:mood:' + str(tidal_mood.id),
                        name=tidal_mood.name)

def to_genres_ref(tidal_genres):
    return [to_genre_ref(m) for m in tidal_genres]

@lru_cache(maxsize=128)
def to_genre_ref(tidal_genre):
    return Ref.playlist(uri='tidal-moppina:genre:' + str(tidal_genre.id),
                        name=tidal_genre.name)

def to_albums_ref(tidal_albums):
    return [to_album_ref(a) for a in tidal_albums]

@lru_cache(maxsize=128)
def to_album_ref(tidal_album):
    return Ref.album(uri='tidal-moppina:album:' + str(tidal_album.id),
                     name=tidal_album.name)

def to_tracks_ref(tidal_tracks):
    return [to_track_ref(t) for t in tidal_tracks]

@lru_cache(maxsize=128)
def to_track_ref(tidal_track):
    uri = 'tidal-moppina:track:{0}:{1}:{2}'.format(tidal_track.artist.id,
                                           tidal_track.album.id,
                                           tidal_track.id)
    return Ref.track(uri=uri, name=tidal_track.name)
