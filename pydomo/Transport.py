from requests.auth import HTTPBasicAuth
from collections import namedtuple
import jsonpickle
import requests
import json


"""
    HTTP Transport via the library 'requests'
    - JSON Serialization via 'jsonpickle'
    - JSON Deserialization via general mapping
    - Authentication with the Domo API is handled automatically (OAuth2)
"""


class DomoAPITransport:
    def __init__(self, client_id, client_secret, api_host, use_https, logger):
        self.apiHost = self._build_apihost(api_host, use_https)
        self.clientId = client_id
        self.clientSecret = client_secret
        self.access_token = ''
        self.logger = logger

    @staticmethod
    def _build_apihost(host, use_https):
        if use_https:
            host = 'https://' + host
        else:
            host = 'http://' + host
        return host

    def get(self, url, params):
        return self.request(url, HTTPMethod.GET, self._headers_receive_json(), params, {})

    def get_csv(self, url, params):
        return self.request(url, HTTPMethod.GET, self._headers_receive_csv(), params, {})

    def post(self, url, body, params):
        return self.request(url, HTTPMethod.POST, self._headers_send_json(), params, self._obj_to_json(body))

    def put(self, url, body):
        return self.request(url, HTTPMethod.PUT, self._headers_send_json(), {}, self._obj_to_json(body))

    def put_csv(self, url, body):
        return self.request(url, HTTPMethod.PUT, self._headers_send_csv(), {}, body)

    def patch(self, url, body):
        return self.request(url, HTTPMethod.PATCH, self._headers_send_json(), {}, self._obj_to_json(body))

    def delete(self, url):
        return self.request(url, HTTPMethod.DELETE, self._headers_receive_json(), {}, {})

    def request(self, url, method, headers, params, body):
        url = self.build_url(url)
        self.logger.info(method + " " + url + "" + str(body))
        return requests.request(method=method, url=url, headers=headers, data=body, params=params)

    def build_url(self, url):
        self.logger.info("URL: " + self.apiHost + url)
        return self.apiHost + url

    @staticmethod
    def _obj_to_json(obj):
        return jsonpickle.encode(obj, unpicklable=False)

    def json_to_obj(self, blob):
        self.logger.info("JSON: " + str(blob))
        return json.loads(blob, object_hook=lambda json_dict: self._filter_reserved_words(json_dict))

    @staticmethod
    def _filter_reserved_words(json_dict):
        keys = list(json_dict.keys())
        i = 0
        for key in keys:
            if key == 'not':
                keys[i] = 'NOT'
            i += 1
        return namedtuple('x', keys)(*json_dict.values())

    def print_json(self, message, json_text):
        self.logger.info(message + ": " + json.dumps(json_text, indent=4))

    def check_renew_token(self):
        if self._token_expired():
            self.access_token = self._renew_access_token()

    def _renew_access_token(self):
        self.logger.info("Renewing Access Token")
        url = self.apiHost + '/oauth/token?grant_type=client_credentials&scope=data user'
        response = requests.post(url=url, auth=HTTPBasicAuth(self.clientId, self.clientSecret))
        if response.status_code == requests.codes.ok:
            return response.json()['access_token']
        else:
            raise Exception("Error retrieving a Domo API Access Token: " + str(response.json()))

    def _token_expired(self):
        token_expired = False
        url = self.apiHost + '/v1/users/'
        response = requests.get(url=url, headers=self._headers_receive_json())
        if response.status_code == requests.codes.unauthorized:
            token_expired = True
        return token_expired

    def _headers_receive_json(self):
        return {
            'Authorization': 'bearer ' + self.access_token,
            'Accept': 'application/json'
        }

    def _headers_send_json(self):
        headers = self._headers_receive_json()
        headers['Content-Type'] = 'application/json'
        return headers

    def _headers_send_csv(self):
        headers = self._headers_receive_json()
        headers['Content-Type'] = 'text/csv'
        return headers

    def _headers_receive_csv(self):
        headers = self._headers_receive_json()
        headers['Accept'] = 'text/csv'
        return headers


class HTTPMethod:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
