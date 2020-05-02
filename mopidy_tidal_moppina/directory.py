from mopidy.models import Ref

from mopidy_tidal_moppina.utils import new_directory_ref

class Directory:

    def __init__(self, uri_scheme):
        self._uri_scheme = uri_scheme
        self._root_uri = f"{uri_scheme}:directory"
        self._directory = {
            self._root_uri: {}
        }
        self.add(new_directory_ref(self._uri_scheme, "Genres", ["genres"]))
        self.add(new_directory_ref(self._uri_scheme, "Moods", ["moods"]))
        self.add(new_directory_ref(self._uri_scheme, "My Artists", ["my_artists"]))
        self.add(new_directory_ref(self._uri_scheme, "My Albumns", ["my_albums"]))
        self.add(new_directory_ref(self._uri_scheme, "My Tracks", ["my_tracks"]))
        # TODO check if playlists also
        # self.add(new_directory("My Artists", ["my_artists"]))

    @property
    def root(self):
        return new_directory_ref(self._uri_scheme, 'Tidal', None)

    def add(self, model):
        self._directory[self._root_uri][model.uri] = model

    def get(self, uri):
        return self._directory.get(uri)

