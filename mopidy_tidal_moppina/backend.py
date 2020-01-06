import logging
import pathlib
import threading

import pykka
from mopidy import backend, httpclient

from tidalapi import Session, Config, Quality

from .playback import TidalMoppinaPlaybackProvider
from .library import TidalMoppinaLibraryProvider

logger = logging.getLogger(__name__)


class TidalMoppinaBackend(pykka.ThreadingActor, backend.Backend):
    
    def __init__(self, config, audio):
        super().__init__()
        self._config = config
        self._audio = audio
        self._session = None
        self._username = self._config['tidal-moppina']['username']
        self._password = self._config['tidal-moppina']['password']
        self._quality = self._config['tidal-moppina']['quality'] or ''
        self.playback = TidalMoppinaPlaybackProvider(audio=audio, backend=self)
        self.library = TidalMoppinaLibraryProvider(backend=self)
        self.playlists = None
        # self.playlists = playlists.TidalPlaylistsProvider(backend=self)
        self.uri_schemes = ['tidal-moppina']

    def on_start(self):
        quality = getattr(Quality, self._quality, Quality.lossless)
        self._session = Session(Config(quality=quality))
        if self._session.login(self._username, self._password):
            logger.info('YaTe -> logged in as %s', self._username)
        else:
            logger.error('YaTe -> Cannot log in user %s', self._username)
