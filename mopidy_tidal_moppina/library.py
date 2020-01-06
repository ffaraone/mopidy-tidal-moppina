import logging

from mopidy import backend, models

from mopidy.models import Image, SearchResult, Ref


from . import utils

from .search import tidal_search


logger = logging.getLogger(__name__)


class TidalMoppinaLibraryProvider(backend.LibraryProvider):
    root_directory = models.Ref.directory(uri='tidal-moppina:directory', name='Tidal')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_distinct(self, field, query=None):
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
        logger.info("Browsing uri %s", uri)
        if not uri or not uri.startswith("tidal-moppina:"):
            return []

        session = self.backend._session

        # summaries

        if uri == self.root_directory.uri:
            return [Ref.directory(uri="tidal-moppina:genres", name="Genres"),
                    Ref.directory(uri="tidal-moppina:moods", name="Moods"),
                    Ref.directory(uri="tidal-moppina:my_artists", name="My Artists"),
                    Ref.directory(uri="tidal-moppina:my_albums", name="My Albums"),
                    Ref.directory(uri="tidal-moppina:my_playlists", name="My Playlists"),
                    Ref.directory(uri="tidal-moppina:my_tracks", name="My Tracks")]

        elif uri == "tidal-moppina:my_artists":
            return utils.to_artists_ref(
                    session.user.favorites.artists())
        elif uri == "tidal-moppina:my_albums":
            return utils.to_albums_ref(
                    session.user.favorites.albums())
        elif uri == "tidal-moppina:my_playlists":
            return utils.to_playlists_ref(
                    session.user.favorites.playlists())
        elif uri == "tidal-moppina:my_tracks":
            return utils.to_tracks_ref(
                    session.user.favorites.tracks())
        elif uri == "tidal-moppina:moods":
            return utils.to_moods_ref(
                    session.get_moods())
        elif uri == "tidal-moppina:genres":
            return utils.to_genres_ref(
                    session.get_genres())

        # details

        parts = uri.split(':')
        nr_of_parts = len(parts)

        # if nr_of_parts == 3 and parts[1] == "album":
        #     return ref_models_mappers.create_tracks(
        #             session.get_album_tracks(parts[2]))

        # if nr_of_parts == 3 and parts[1] == "artist":
        #     top_10_tracks = session.get_artist_top_tracks(parts[2])[:10]
        #     albums = ref_models_mappers.create_albums(
        #             session.get_artist_albums(parts[2]))
        #     return albums + ref_models_mappers.create_tracks(top_10_tracks)

        # if nr_of_parts == 3 and parts[1] == "playlist":
        #     return ref_models_mappers.create_tracks(
        #         session.get_playlist_tracks(parts[2]))

        # if nr_of_parts == 3 and parts[1] == "mood":
        #     return ref_models_mappers.create_playlists(
        #         session.get_mood_playlists(parts[2]))

        # if nr_of_parts == 3 and parts[1] == "genre":
        #     return ref_models_mappers.create_playlists(
        #         session.get_genre_items(parts[2], 'playlists'))

        logger.debug('Unknown uri for browse request: %s', uri)
        return []

    def search(self, query=None, uris=None, exact=False):
        try:
            artists, albums, tracks = \
                tidal_search(self.backend._session,
                             query=query,
                             exact=exact)
            return SearchResult(artists=artists,
                                albums=albums,
                                tracks=tracks)
        except Exception as ex:
            logger.info("EX")
            logger.info("%r", ex)

    def get_images(self, uris):
        logger.debug("Searching Tidal for images for %r" % uris)
        session = self.backend._session
        images = {}
        # for uri in uris:
        #     uri_images = None
        #     if uri.startswith('tidal-moppina:'):
        #         parts = uri.split(':')
        #         if parts[1] == 'artist':
        #             artist_id = parts[2]
        #             img_uri = self.lru_artist_img.hit(artist_id)
        #             if img_uri is None:
        #                 artist = session.get_artist(artist_id)
        #                 img_uri = artist.image
        #                 self.lru_artist_img[artist.id] = img_uri

        #             uri_images = [Image(uri=img_uri, width=512, height=512)]
        #         elif parts[1] == 'album':
        #             album_id = parts[2]
        #             img_uri = self.lru_album_img.hit(album_id)
        #             if img_uri is None:
        #                 album = session.get_album(album_id)
        #                 img_uri = album.image
        #                 self.lru_album_img[album_id] = img_uri

        #             uri_images = [Image(uri=img_uri, width=512, height=512)]
        #         elif parts[1] == 'track':
        #             album_id = parts[3]
        #             img_uri = self.lru_album_img.hit(album_id)
        #             if img_uri is None:
        #                 album = session.get_album(album_id)
        #                 img_uri = album.image
        #                 self.lru_album_img[album_id] = img_uri

        #             uri_images = [Image(uri=img_uri, width=512, height=512)]
        #             pass

        #     images[uri] = uri_images or ()
        return images

    def lookup(self, uris=None):
        logger.info("Lookup uris %r", uris)
        session = self.backend._session
        if isinstance(uris, str):
            uris = [uris]

        tracks = []
        for uri in uris:
            parts = uri.split(':')
            logger.debug('YaTe -> uri=%s, parts=%s', uri, parts)
            if uri.startswith('tidal-moppina:track:'):
                tracks += self._lookup_track(session, parts)
            elif uri.startswith('tidal-moppina:album'):
                tracks += self._lookup_album(session, parts)
            elif uri.startswith('tidal-moppina:artist'):
                tracks += self._lookup_artist(session, parts)

        logger.info("Returning %d tracks", len(tracks))
        return tracks

    def _lookup_track(self, session, parts):
        album_id = parts[3]
        tracks = session.get_album_tracks(album_id)

        track = [t for t in tracks if t.id == int(parts[4])][0]
        artist = utils.to_artist(track.artist)
        album = utils.to_album(track.album, artist)
        return [utils.to_track(artist, album, track)]

    def _lookup_album(self, session, parts):
        album_id = parts[2]
        logger.debug('YaTe -> lookup album %s', album_id)
        tracks = session.get_album_tracks(album_id)
        return utils.to_tracks(tracks)

    def _lookup_artist(self, session, parts):
        artist_id = parts[2]
        artist_tracks = session.get_artist_top_tracks(artist_id)
        return utils.to_tracks(artist_tracks)
