import logging
from hashlib import sha256
from mopidy import backend, models
from mopidy.models import Image, Ref, SearchResult

from mopidy_tidal_moppina.directory import Directory
from mopidy_tidal_moppina.utils import (new_album_image, new_album_ref,
                                        new_artist_image, new_artist_ref,
                                        new_track_ref, new_album, new_track, new_artist)

# from . import utils
# from .search import tidal_search

logger = logging.getLogger(__name__)




class TidalMoppinaLibraryProvider(backend.LibraryProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uri_scheme = self.backend.uri_schemes[0]
        self._directory = Directory(self._uri_scheme)
        self._tidal = self.backend.get_tidal()
        self.root_directory = self._directory.root


    def get_distinct(self, field, query=None):
        logger.debug('get_distict field=%s, query=%s', field, query)
        # logger.debug("Browsing distinct %s with query %r", field, query)
        # session = self.backend._session

        # if not query:  # library root
        #     if field == "artist" or field == "albumartist":
        #         return [apply_watermark(a.name) for a in
        #                 session.user.favorites.artists()]
        #     elif field == "album":
        #         return [apply_watermark(a.name) for a in
        #                 session.user.favorites.albums()]
        #     elif field == "track":
        #         return [apply_watermark(t.name) for t in
        #                 session.user.favorites.tracks()]
        # else:
        #     if field == "artist":
        #         return [apply_watermark(a.name) for a in
        #                 session.user.favorites.artists()]
        #     elif field == "album" or field == "albumartist":
        #         artists, _, _ = tidal_search(session,
        #                                      query=query,
        #                                      exact=True)
        #         if len(artists) > 0:
        #             artist = artists[0]
        #             artist_id = artist.uri.split(":")[2]
        #             return [apply_watermark(a.name) for a in
        #                     session.get_artist_albums(artist_id)]
        #     elif field == "track":
        #         return [apply_watermark(t.name) for t in
        #                 session.user.favorites.tracks()]
        #     pass

        return []
    def browse(self, uri):
        if not uri or not uri.startswith(self._uri_scheme):
            return []

        if uri == self.root_directory.uri:
            return list(self._directory.get(uri).values())

        _, ref_type, path = uri.split(':', 2)
        if ref_type == 'directory':
            if path == 'my_artists':
                data = self._tidal.my_artists()
                my_artists = [
                    new_artist_ref(
                        self._uri_scheme, 
                        artist['item']['name'],
                        [str(artist['item']['id'])],
                    )
                    for artist in data
                ]
                return my_artists
        if ref_type == 'artist':
            data = self._tidal.artist_albums(path)
            albums = [
                new_album_ref(
                    self._uri_scheme,
                    album['title'],
                    [str(album['id'])],
                )
                for album in data
            ]
            return albums
        if ref_type == 'album':
            data = self._tidal.album_tracks(path)
            tracks = [
                new_track_ref(
                    self._uri_scheme,
                    track['title'],
                    [str(track['id'])],
                )
                for track in data
            ]
            logger.debug('tracks of album %s=%s', path, tracks)
            return tracks
        return []

    def _get_track(self, track):
        return new_track(
            self._uri_scheme,
            track['title'],
            [str(track['id'])],
            artists=[
                self._get_artist(artist)
                for artist in track['artists']
            ],
            album=self._get_album(track['album']),
            disc_no=track['volumeNumber'],
            track_no=track['trackNumber'],
            length=track['duration'] * 1000,
        )

    def _get_album(self, album):
        return new_album(
            self._uri_scheme,
            album['title'],
            [str(album['id'])],
            artists=[
                self._get_artist(artist)
                for artist in album.get('artists', [])
            ],
            num_tracks=album.get('numberOfTracks', 0),
            num_discs=album.get('numberOfVolumes', 0),
            date=album.get('releaseDate', '')
        )

    def _get_artist(self, artist):
        return new_artist(
            self._uri_scheme,
            artist['name'],
            [str(artist['id'])]
        )

    def _perform_search(self, field, query):
        keywords = query[field]
        search_query = ' '.join(keywords)
        search_id = sha256(bytes(search_query, encoding='utf-8')).hexdigest()
        data = self._tidal.search(field, search_query)
        method = getattr(self, f"_get_{field}")
        results = [ method(item) for item in data ]
        kwargs = {
            "artists": [],
            "albums": [],
            "tracks": [],
        }
        kwargs[f"{field}s"] = results
        return SearchResult(**kwargs)

    def search(self, query=None, uris=None, exact=False):
        # TODO check if query is for me
        logger.debug('query=%s, uris=%s, exact=%s', query, uris, exact)
        for (field, values) in query.items():
            if not hasattr(values, '__iter__'):
                values = [values]
            search_val = values[0]
            return SearchResult(
                albums=self._perform_search('album', {'album': search_val}).albums,
                artists=self._perform_search('artist', {'artist': search_val}).artists,
                tracks=self._perform_search('track', {'track': search_val}).tracks,
            )
        
        # if 'any' in query:
        #     pass
        #     # query['album'] = query['any']
        #     # query['artist'] = query['any']
        #     # query['track'] = query['any']
        #     # res = SearchResult(
        #     #     uri='tidal-moppina:search:any',

        #     # )
        #     # return res
        # if 'album' in query:
        #     return self._perform_search('album', query)
        # if 'artist' in query:
        #     res = self._perform_search('artist', query)
        #     logger.info(res.artists)
        #     # return self._perform_search('artist', query)

        return SearchResult(artists=[], albums=[], tracks=[])

    def get_images(self, uris):
        logger.debug("Searching Tidal for images for %s" % uris)
        if not uris:
            return {}
        images = {}
        for uri in uris:
            if not uri.startswith(self._uri_scheme):
                continue
            sub_uri = uri[len(self._uri_scheme) + 1:]
            if sub_uri.startswith('directory'):
                continue
            ref_type, obj_id = sub_uri.split(':', 1)
            logger.debug('retries %s (%s)', ref_type, obj_id)
            if ref_type == 'artist':
                images[uri] = [new_artist_image(obj_id)]
            if ref_type == 'album':
                images[uri] = [new_album_image(obj_id)]

        return images

    def lookup(self, uris=None):
        try:
            # logger.info("Lookup uris %r", uris)
            if isinstance(uris, str):
                uris = [uris]

            tracks = []
            for uri in uris:
                _, ref_type, obj_id = uri.split(':', 2)
               
                if ref_type == 'track':
                    track = self._tidal.track(obj_id)
                    artists = [
                        self._get_artist(artist)
                        for artist in track['artists']
                    ]
                    track = new_track(
                        self._uri_scheme,
                        track['title'],
                        [str(track['id'])],
                        artists=artists,
                        album=self._get_album(track['album']),
                        disc_no=track['volumeNumber'],
                        track_no=track['trackNumber'],
                        length=track['duration'] * 1000,
                    )
                    return [track]
                if ref_type == 'album':
                    tracks = self._tidal.album_tracks(obj_id)
                    return [
                        self._get_track(track)
                        for track in tracks
                    ]
        except Exception:
            logger.exception('cannot lookup uris %s', uris)
