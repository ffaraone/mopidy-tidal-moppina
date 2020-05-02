import logging
import pathlib
import threading

import pykka
from mopidy import backend, httpclient

from tidalapi import Session, Config, Quality

from mopidy_tidal_moppina.playback import TidalMoppinaPlaybackProvider
from mopidy_tidal_moppina.library import TidalMoppinaLibraryProvider
from mopidy_tidal_moppina.tidal import TidalClient

logger = logging.getLogger(__name__)


class TidalMoppinaBackend(pykka.ThreadingActor, backend.Backend):
    
    def __init__(self, config, audio):
        super().__init__()
        self._config = config
        self._audio = audio
        self.uri_schemes = ['tidal-moppina']
        self._username = self._config['tidal-moppina']['username']
        self._password = self._config['tidal-moppina']['password']
        self._quality = self._config['tidal-moppina']['quality'] or ''
        self._tidal = TidalClient(self._username, self._password)
        self.playback = TidalMoppinaPlaybackProvider(audio=audio, backend=self)
        self.library = TidalMoppinaLibraryProvider(backend=self)
        self.playlists = None
        # self.playlists = playlists.TidalPlaylistsProvider(backend=self)
        
    def on_start(self):
        self._tidal.login()
        logger.info('Tidal-Moppina started')

    def get_tidal(self):
        return self._tidal
