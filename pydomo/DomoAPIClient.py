import json
import requests
import zlib

from pydomo.Transport import HTTPMethod

class DomoAPIClient(object):
    """DomoAPIClient
    Each API client class inherits from this superclass
    """

    def __init__(self, transport, logger):
        self.transport = transport
        self.logger = logger

    def _create(self, url, request, params, obj_desc):
        response = self.transport.post(url=url, params=params, body=request)
        if response.status_code in (requests.codes.CREATED, requests.codes.OK):
            obj = response.json()
            self.print_json("Created", obj)
            return obj
        else:
            self.logger.debug("Error creating " + obj_desc + ": "
                              + self.transport.dump_response(response))
            raise Exception("Error creating " + obj_desc + ": " + response.text)

    def _get(self, url, obj_desc):
        response = self.transport.get(url=url, params={})
        if response.status_code == requests.codes.OK:
            return response.json()
        else:
            self.logger.debug("Error retrieving " + obj_desc + ": "
                              + self.transport.dump_response(response))
            raise Exception("Error retrieving " + obj_desc + ": "
                            + response.text)

    def _update(self, url, method, success_code, obj_update, obj_desc):
        if method == HTTPMethod.PUT:
            response = self.transport.put(url, obj_update)
        elif method == HTTPMethod.PATCH:
            response = self.transport.patch(url, obj_update)
        if response.status_code == success_code:
            if str(response.text) == '':
                return
            else:
                obj = response.json()
                self.print_json("Updated", obj)
                return obj
        else:
            self.logger.debug("Error updating " + obj_desc + ": "
                              + self.transport.dump_response(response))
            raise Exception("Error updating " + obj_desc + ": "
                            + response.text)

    def _list(self, url, params, obj_desc):
        response = self.transport.get(url=url, params=params)
        if response.status_code == requests.codes.OK:
            return response.json()
        else:
            self.logger.debug(obj_desc + " Error: "
                              + self.transport.dump_response(response))
            raise Exception(obj_desc + " Error: " + response.text)

    def _delete(self, url, obj_desc):
        response = self.transport.delete(url=url)
        if response.status_code == requests.codes.NO_CONTENT:
            return
        else:
            self.logger.debug("Error deleting " + obj_desc + ": "
                              + self.transport.dump_response(response))
            raise Exception("Error deleting " + obj_desc + ": "
                            + response.text)

    def _upload_csv(self, url, success_code, csv, obj_desc):
        response = self.transport.put_csv(url=url, body=csv)
        if response.status_code == success_code:
            if str(response.text) == '':
                return
            else:
                return response.json()
        else:
            self.logger.debug("Error uploading " + obj_desc + ": " + self.transport.dump_response(response))
            raise Exception("Error uploading " + obj_desc + ": "
                            + response.text)

    def _upload_gzip(self, url, success_code, csv, obj_desc):
        post_data = zlib.compress(csv.read())
        response = self.transport.put_gzip(url=url, body=post_data)
        if response.status_code == success_code:
            if str(response.text) == '':
                return
            else:
                return response.json()
        else:
            self.logger.debug("Error uploading " + obj_desc + ": " + self.transport.dump_response(response))
            raise Exception("Error uploading " + obj_desc + ": "
                            + response.text)

    def _download_csv(self, url, include_csv_header):
        params = {
            'includeHeader': str(include_csv_header)
        }
        return self.transport.get_csv(url=url, params=params)

    def _validate_params(self, params, accepted_keys):
        bad_keys = list(set(params.keys()).difference(accepted_keys))
        if bad_keys:
           raise TypeError('Unexpected keyword arguments: {}'.format(bad_keys))

    def _base(self, obj_id):
        return self.urlBase + str(obj_id)

    def print_json(self, message, json_obj):
        self.logger.info(message + ": " + json.dumps(json_obj, indent=4))
