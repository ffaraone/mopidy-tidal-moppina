import logging

from mopidy import backend

logger = logging.getLogger(__name__)


class TidalMoppinaPlaybackProvider(backend.PlaybackProvider):

    def translate_uri(self, uri):
        logger.info('YaTe -> uri: %s', uri)
        parts = uri.split(':')
        track_id = int(parts[4])
        url = self.backend._session.get_media_url(track_id)
        logger.info("YaTe -> Tidal uri: %s", url)
        return url
