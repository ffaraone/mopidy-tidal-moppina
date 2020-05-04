import logging
import urllib.parse

from functools import lru_cache, partial
from mopidy import models

logger = logging.getLogger(__name__)


def _new_image(id, id_type):
    return models.Image(
        uri=f"http://images.osl.wimpmusic.com/im/im?w=512&h=512&{id_type}={id}",
        width=512,
        height=512,
    )

new_artist_image = partial(_new_image, id_type='artistid')
new_album_image = partial(_new_image, id_type='albumid')


def generate_uri(scheme, uri_type, path):
    if not path:
        return f"{scheme}:{uri_type}"
    return f"{scheme}:{uri_type}:{''.join(path)}"

def _new_ref(scheme, name, path, ref_type=None):
    # logger.debug('scheme=%s name=%s path=%s ref_type=%s', scheme, name, path, ref_type)
    ref = getattr(models.Ref, ref_type)
    return ref(uri=generate_uri(scheme, ref_type, path), name=name)

new_directory_ref = partial(_new_ref, ref_type='directory')
new_artist_ref = partial(_new_ref, ref_type='artist')
new_album_ref = partial(_new_ref, ref_type='album')
new_track_ref = partial(_new_ref, ref_type='track')

def _new_model(scheme, name, path, model_type=None, **kwargs):
    model = getattr(models, model_type)
    return model(uri=generate_uri(scheme, model_type.lower(), path), name=name, **kwargs)

# new_artist = partial(_new_model, model_type='Artist')
new_album = partial(_new_model, model_type='Album')
new_track = partial(_new_model, model_type='Track')

def new_artist(scheme, name, path):
    artist = models.Artist(
        uri='tidal-moppina:artist:{}'.format(''.join(path)),
        name=name
    )
    logger.warn(path)
    return artist