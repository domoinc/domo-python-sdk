from pydomo.Transport import HTTPMethod
import requests

"""
    DomoAPIClient
    - Each API client class inherits from this superclass
"""


class DomoAPIClient:
    def __init__(self, transport, logger):
        self.transport = transport
        self.logger = logger

    def _create(self, url, request, params, obj_desc):
        response = self.transport.post(url=url, params=params, body=request)
        if response.status_code == requests.codes.created or response.status_code == requests.codes.ok:
            obj = self.transport.json_to_obj(response.text)
            self.transport.print_json("Created", str(response.json()))
            return obj
        else:
            raise Exception("Error creating " + str(obj_desc) + ": " + self.transport.dump_response(response))

    def _get(self, url, obj_desc):
        response = self.transport.get(url=url, params={})
        if response.status_code == requests.codes.ok:
            obj = self.transport.json_to_obj(response.text)
            return obj
        else:
            raise Exception("Error retrieving " + str(obj_desc) + ": " + self.transport.dump_response(response))

    def _update(self, url, method, success_code, obj_update, obj_desc):
        response = ''
        if method == HTTPMethod.PUT:
            response = self.transport.put(url, obj_update)
        elif method == HTTPMethod.PATCH:
            response = self.transport.patch(url, obj_update)
        if response.status_code == success_code:
            if str(response.text) == '':
                return
            else:
                obj = self.transport.json_to_obj(response.text)
                self.transport.print_json("Updated", str(response.json()))
                return obj
        else:
            raise Exception("Error updating " + str(obj_desc) + ": " + self.transport.dump_response(response))

    def _list(self, url, params, obj_desc):
        response = self.transport.get(url=url, params=params)
        if response.status_code == requests.codes.ok:
            obj_list = self.transport.json_to_obj(response.text)
            return obj_list
        else:
            raise Exception(obj_desc + " Error: " + self.transport.dump_response(response))

    def _delete(self, url, obj_desc):
        response = self.transport.delete(url=url)
        if response.status_code == requests.codes.no_content:
            return
        else:
            raise Exception("Error deleting " + str(obj_desc) + ": " + self.transport.dump_response(response))

    def _upload_csv(self, url, success_code, csv, obj_desc):
        response = self.transport.put_csv(url=url, body=csv)
        if response.status_code == success_code:
            if str(response.text) == '':
                return
            else:
                return self.transport.json_to_obj(response.text)
        else:
            raise Exception("Error uploading " + str(obj_desc) + ": " + self.transport.dump_response(response))

    def _upload_compressed_csv(self, url, success_code, zipped_csv, obj_desc):
        response = self.transport.put_csv_gzip(url=url, zipped_csv=zipped_csv)
        if response.status_code == success_code:
            if str(response.text) == '':
                return
            else:
                return self.transport.json_to_obj(response.text)
        else:
            raise Exception("Error uploading " + str(obj_desc) + ": " + self.transport.dump_response(response))

    def _base(self, obj_id):
        return self.urlBase + str(obj_id)
