import requests
import json
from collections import namedtuple
from requests.auth import HTTPBasicAuth
from requests_toolbelt.utils import dump


class DomoAPITransport:
    """Essentially a wrapper around the 'requests' library to make
    it easier to interact with the Domo API.

    OAuth2 authentication is handled automatically, as well as the
    serialization and deserialization of objects.
    """

    def __init__(self, client_id, client_secret, api_host, use_https, logger, request_timeout):
        self.apiHost = self._build_apihost(api_host, use_https)
        self.clientId = client_id
        self.clientSecret = client_secret
        self.logger = logger
        self._renew_access_token()
        self.request_timeout = request_timeout

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
        response = requests.request(**request_args)
        if response.status_code == requests.codes.UNAUTHORIZED:
            self._renew_access_token()
            headers['Authorization'] = 'bearer ' + self.access_token
            response = requests.request(**request_args)
        return response

    def _renew_access_token(self):
        self.logger.debug("Renewing Access Token")
        url = self.apiHost + '/oauth/token?grant_type=client_credentials'
        response = requests.post(url=url, auth=HTTPBasicAuth(self.clientId, self.clientSecret))
        if response.status_code == requests.codes.OK:
            self.access_token = response.json()['access_token']
        else:
            self.logger.debug('Error retrieving access token: ' + self.dump_response(response))
            raise Exception("Error retrieving a Domo API Access Token: " + response.text)

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
