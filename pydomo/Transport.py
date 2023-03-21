import requests
import json
import base64
from collections import namedtuple
from requests.auth import HTTPBasicAuth
from requests_toolbelt.utils import dump
from datetime import datetime, timezone


class DomoAPITransport:
    """Essentially a wrapper around the 'requests' library to make
    it easier to interact with the Domo API.

    OAuth2 authentication is handled automatically, as well as the
    serialization and deserialization of objects.
    """

    def __init__(self, client_id, client_secret, api_host, use_https, logger, request_timeout, proxies, verify):
        self.apiHost = self._build_apihost(api_host, use_https)
        self.clientId = client_id
        self.clientSecret = client_secret
        self.logger = logger
        self.request_timeout = request_timeout
        self.proxies = proxies
        self.verify = verify
        self._renew_access_token()

    @staticmethod
    def _build_apihost(host, use_https):
        if use_https:
            host = 'https://' + host
        else:
            host = 'http://' + host
        return host

    def get(self, url, params):
        headers = self._headers_default_receive_json()
        return self.request(url, HTTPMethod.GET, headers, params)

    def get_csv(self, url, params):
        headers = self._headers_receive_csv()
        return self.request(url, HTTPMethod.GET, headers, params)

    def post(self, url, body, params):
        headers = self._headers_send_json()
        return self.request(url, HTTPMethod.POST, headers, params,
                            self._obj_to_json(body))

    def put(self, url, body):
        headers = self._headers_send_json()
        return self.request(url, HTTPMethod.PUT, headers, {},
                            self._obj_to_json(body))

    def put_csv(self, url, body):
        headers = self._headers_send_csv()
        return self.request(url, HTTPMethod.PUT, headers, {}, body)

    def put_gzip(self, url, body):
        headers = self._headers_send_gzip()
        return self.request(url, HTTPMethod.PUT, headers, {}, body)

    def patch(self, url, body):
        headers = self._headers_send_json()
        return self.request(url, HTTPMethod.PATCH, headers, {},
                            self._obj_to_json(body))

    def delete(self, url):
        headers = self._headers_default_receive_json()
        return self.request(url, HTTPMethod.DELETE, headers)

    def request(self, url, method, headers, params=None, body=None):
        url = self.apiHost + url
        self.logger.debug('{} {} {}'.format(method, url, body))
        request_args = {'method': method, 'url': url, 'headers': headers,
                        'params': params, 'data': body, 'stream': True}
        if self.request_timeout:
            request_args['timeout'] = self.request_timeout
        if self.proxies:
            request_args['proxies'] = self.proxies
        if self.verify is not None:
            request_args['verify'] = self.verify
        # Expiration date should be in UTC
        if datetime.now(timezone.utc).timestamp() > self.token_expiration:
            self.logger.debug("Access token is expired")
            self._renew_access_token()
            headers['Authorization'] = 'bearer ' + self.access_token

        return requests.request(**request_args)

    def _renew_access_token(self):
        self.logger.debug("Renewing Access Token")
        request_args = {
            'method': HTTPMethod.POST,
            'url': self.apiHost + '/oauth/token?grant_type=client_credentials',
            'auth': HTTPBasicAuth(self.clientId, self.clientSecret)
        }
        if self.request_timeout:
            request_args['timeout'] = self.request_timeout
        if self.proxies:
            request_args['proxies'] = self.proxies
        if self.verify is not None:
            request_args['verify'] = self.verify

        response = requests.request(**request_args)
        if response.status_code == requests.codes.OK:
            self.access_token = response.json()['access_token']
            self.token_expiration = self._extract_expiration(self.access_token)
        else:
            self.logger.debug('Error retrieving access token: ' + self.dump_response(response))
            raise Exception("Error retrieving a Domo API Access Token: " + response.text)

    def _extract_expiration(self, access_token):
        expiration_date = 0
        try:
            decoded_payload_dict = self._decode_payload(access_token)

            if 'exp' in decoded_payload_dict.keys():
                expiration_date = decoded_payload_dict['exp']
                self.logger.debug('Token expiration: {}'
                                  .format(expiration_date))
        except Exception as err:
            # If an Exception is raised, log and continue. expiration_date will
            # either be 0 or set to the value in the JWT.
            self.logger.debug('Ran into error parsing token for expiration. '
                              'Setting expiration date to 0. '
                              '{}: {}'.format(type(err).__name__, err))
        return expiration_date

    def _decode_payload(self, access_token):
        token_parts = access_token.split('.')

        # Padding required for the base64 library
        payload_bytes = bytes(token_parts[1], 'utf-8') + b'=='
        decoded_payload_bytes = base64.urlsafe_b64decode(payload_bytes)
        payload_string = decoded_payload_bytes.decode('utf-8')
        return json.loads(payload_string)

    def dump_response(self, response):
        data = dump.dump_all(response)
        return str(data.decode('utf-8'))

    @staticmethod
    def _obj_to_json(obj):
        return json.dumps(obj, default=str)

    def _headers_default_receive_json(self):
        return {
            'Authorization': 'bearer ' + self.access_token,
            'Accept': 'application/json'
        }

    def _headers_send_json(self):
        headers = self._headers_default_receive_json()
        headers['Content-Type'] = 'application/json'
        return headers

    def _headers_send_csv(self):
        headers = self._headers_default_receive_json()
        headers['Content-Type'] = 'text/csv'
        return headers

    def _headers_send_gzip(self):
        headers = self._headers_default_receive_json()
        headers['Content-Type'] = 'text/csv'
        headers['Content-Encoding'] = 'gzip'
        return headers

    def _headers_receive_csv(self):
        headers = self._headers_default_receive_json()
        headers['Accept'] = 'text/csv'
        return headers


class HTTPMethod:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
