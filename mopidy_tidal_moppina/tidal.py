import logging
from pprint import pformat
import requests
from mopidy import httpclient

from mopidy_tidal_moppina.cache import cache
from mopidy_tidal_moppina.utils import new_artist_ref


logger = logging.getLogger(__name__)


def get_requests_session(proxy_config, user_agent, token):
    proxy = httpclient.format_proxy(proxy_config)
    full_user_agent = httpclient.format_user_agent(user_agent)

    session = requests.Session()
    session.proxies.update({"http": proxy, "https": proxy})
    session.headers.update({"user-agent": full_user_agent})

    return session


class TidalClient:

    def __init__(self, username, password, limit=50):
        self._username = username
        self._password = password
        self._api_location = "https://api.tidalhifi.com/v1"
        self._api_token = "kgsOOmYk3zShYrNP"
        self._session_id = None
        self._country_code = None
        self._user_id = None
        self._base_uri = None
        self._limit = limit

    def login(self):
        url = f"{self._api_location}/login/username"
        params = {'token': self._api_token}
        payload = {
            'username': self._username,
            'password': self._password,
        }
        response = requests.post(url, data=payload, params=params)
        data = self._check_response(response)
        self._session_id = data.get('sessionId')
        self._country_code = data.get('countryCode')
        self._user_id = data.get('userId')
        self._favorites_uri = f"{self._api_location}/users/{self._user_id}/favorites"
        logger.info('Login succeded: userId=%s', self._user_id)

    def _check_response(self, response):
        data = response.json()
        if not response.ok:
            logger.error(
                "Cannot logging in: status=%s, code=%s msg=%s",
                data.get('status'),
                data.get('subStatus'),
                data.get('userMessage'),
            )
            # TODO check how to raise error in mopidy
            response.raise_for_status()
        return data

    def _get_request_params(self):
        return {
            'sessionId': self._session_id,
            'countryCode': self._country_code,
            'limit': f'{self._limit}',
        }

    def get_playlists(self):
        url = f"{self._favorites_uri}/playlists"
        params = self._get_request_params()
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('playlists=%s', data)
        return data
        
    @cache(ttl=10)
    def my_artists(self):
        url = f"{self._favorites_uri}/artists"
        params = self._get_request_params()
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('artists=%s', data)    
        return data.get('items', [])

    @cache()
    def artist(self, artist_id):
        url = f"{self._api_location}/artists/{artist_id}"
        params = self._get_request_params()
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('artist=%s', data)
        return data

    @cache()
    def track(self, track_id):
        url = f"{self._api_location}/tracks/{track_id}"
        params = self._get_request_params()
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('track=%s', pformat(data, indent=2, compact=False))
        return data

    @cache()
    def artist_albums(self, artist_id):
        url = f"{self._api_location}/artists/{artist_id}/albums"
        params = self._get_request_params()
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('albums=%s', data)
        return data.get('items', [])

    @cache()
    def album_tracks(self, album_id):
        url = f"{self._api_location}/albums/{album_id}/tracks"
        params = self._get_request_params()
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('tracks=%s', data)
        return data.get('items', [])

    @cache()
    def album(self, album_id):
        url = f"{self._api_location}/albums/{album_id}"
        params = self._get_request_params()
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('album=%s', data)
        return data


    def search(self, obj_type, keywords):
        url = f"{self._api_location}/search/{obj_type}s"
        params = self._get_request_params()
        params['query'] = keywords
        response = requests.get(url, params=params)
        data = self._check_response(response)
        # logger.debug('search=%s', data)
        return data.get('items', [])

    # def artists(self):
    #     return self._session._map_request(self._base_url + '/artists', ret='artists')

    # def albums(self):
    #     return self._session._map_request(self._base_url + '/albums', ret='albums')

    # def playlists(self):
    #     return self._session._map_request(self._base_url + '/playlists', ret='playlists')

    # def tracks(self):
    #     request = self._session.request('GET', self._base_url + '/tracks')
    #     return [_parse_media(item['item']) for item in request.json()['items']]