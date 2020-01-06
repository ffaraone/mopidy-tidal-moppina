import logging

from threading import Thread

from .utils import to_albums, to_artists, to_tracks

logger = logging.getLogger(__name__)


def tidal_search(session, query, exact):
    logger.info('Searching Tidal for: %s %r', "Exact" if exact else "", query)
    for (field, values) in query.items():
        if not hasattr(values, '__iter__'):
            values = [values]

        search_val = values[0]
        if field in ['track_name', 'album', 'artist', 'albumartist', 'any']:
            if exact:
                exact_search = TidalExactSearchThread(session, search_val,
                                                      field)
                exact_search.start()
                exact_search.join()
                results = exact_search.results
            else:
                artist_search = TidalSearchThread(session, search_val,
                                                  "artist")
                artist_search.start()
                album_search = TidalSearchThread(session, search_val,
                                                 "album")
                album_search.start()
                track_search = TidalSearchThread(session, search_val,
                                                 "track")
                track_search.start()
                artist_search.join()
                album_search.join()
                track_search.join()
                results = artist_search.results, \
                    album_search.results, \
                    track_search.results

            return results

        return [], [], []


class TidalSearchThread(Thread):
    def __init__(self, session, keyword, kind):
        super(TidalSearchThread, self).__init__()
        self.results = []
        self.session = session
        self.keyword = keyword
        self.kind = kind

    def run(self):
        if self.kind == "artist":
            artists = self.session.search("artist", self.keyword).artists
            self.results = to_artists(artists)
        elif self.kind == "album":
            albums = self.session.search("album", self.keyword).albums
            self.results = to_albums(albums)
        elif self.kind == "track":
            tracks = self.session.search("track", self.keyword).tracks
            self.results = to_tracks(tracks)


class TidalExactSearchThread(TidalSearchThread):
    def __init__(self, session, keyword, kind):
        super(TidalExactSearchThread, self).__init__(session, keyword, kind)
        self.artists = []
        self.albums = []
        self.tracks = []
        self.results = [], [], []

    def run(self):
        if self.kind == "album":
            self.search_album()
        elif self.kind == "artist":
            self.search_artist()

        self.results = self.artists, self.albums, self.tracks

    def search_album(self):
        res = self.session.search("album", self.keyword).albums
        album = next((a for a in res
                      if a.name.lower() == self.keyword.lower()), None)
        logger.info("Album not found" if album is None else "Album found OK")
        if album:
            self.albums = to_albums([album])
            tracks = self.session.get_album_tracks(album.id)
            self.tracks = to_tracks(tracks)
            logger.info("Found %d tracks for album", len(self.tracks))

    def search_artist(self):
        res = self.session.search("artist", self.keyword).artists
        logger.info("Found %d artists", len(res))
        for artist in res:
            if artist.name.lower() == self.keyword.lower():
                logger.info("Artist match OK")
                self.artists = to_artists([artist])
                break
