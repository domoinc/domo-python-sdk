from pydomo.Transport import DomoAPITransport
from pydomo.datasets import DataSetClient
from pydomo.datasets import DataSetRequest
from pydomo.datasets import Schema
from pydomo.datasets import Column
from pydomo.datasets import ColumnType
from pydomo.groups import GroupClient
from pydomo.pages import PageClient
from pydomo.streams import StreamClient
from pydomo.users import UserClient
from pydomo.users import CreateUserRequest
from pydomo.accounts import AccountClient
from pydomo.utilities import UtilitiesClient
from pandas import read_csv
from pandas import DataFrame
from pandas import to_datetime
from io import StringIO
import logging
import json
import csv

DOMO = """####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
             ``.############.`          `.###### `#######################``######.`         ``.#####
                 .#######.`                `.###   .###################`   ###.`                `###
    #######..`     .####`     ..######.`     `##     .###############`     ##`     ..######.`     `#
    ###########`    .##     .############.    `#       .###########`       #     .############.
    ############.    #`   `################    `         .#######.         `   `################
    #############`        #################.        ``     .###.     ``        #################.
    #############`        ##################        .##`     `     `##`        ##################
    #############`        #################.        .####`       `####`        #################.
    ############.    #`   `################    `    .######`   `######`    `   `################
    ###########`    .##     .############.     #    .########`########`    #     .############.
    #######..`     .####`     ########.`     `##    .#################`    ##`     ..######.`     `#
                 .#######.`                `.###    .#################`    ###.`                `.##
               .############.`          `.######    .#################`    ######.`          `.#####
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################"""

parent_logger = logging.getLogger('pydomo')
parent_logger.setLevel(logging.WARNING)


class Domo:
    def __init__(self, client_id, client_secret, api_host='api.domo.com', **kwargs):
        if 'logger_name' in kwargs:
            self.logger = parent_logger.getChild(kwargs['logger_name'])
        else:
            self.logger = parent_logger

        timeout = kwargs.get('request_timeout', None)
        scope = kwargs.get('scope')

        if kwargs.get('log_level'):
            self.logger.setLevel(kwargs['log_level'])
        self.logger.debug("\n" + DOMO + "\n")

        self.transport = DomoAPITransport(client_id, client_secret, api_host, kwargs.get('use_https', True), self.logger, request_timeout = timeout, scope = scope)
        self.datasets = DataSetClient(self.transport, self.logger)
        self.groups = GroupClient(self.transport, self.logger)
        self.pages = PageClient(self.transport, self.logger)
        self.streams = StreamClient(self.transport, self.logger)
        self.users = UserClient(self.transport, self.logger)
        self.accounts = AccountClient(self.transport, self.logger)
        self.utilities = UtilitiesClient(self.transport, self.logger)

######### Datasets #########
    def ds_meta(self, dataset_id):
        """
            Get a DataSet metadata

            :Parameters:
            - `dataset_id`: id of a dataset (str)

            :Returns:
            - A dict representing the dataset meta-data
        """
        return self.datasets.get(dataset_id)

    def ds_delete(self, dataset_id, prompt_before_delete=True):
        """
            Delete a DataSet naming convention equivalent with rdomo

            :Parameters:
            - `dataset_id`: id of a dataset (str)
        """

        del_data = 'Y'
        if prompt_before_delete:
            del_data = input("Permanently delete this data set? This is destructive and cannot be reversed. (Y/n)")

        out = 'Data set not deleted'
        if del_data == 'Y':
            out = self.datasets.delete(dataset_id)

        return out

    def ds_list(self, df_output = True, per_page=50, offset=0, limit=0, name_like=""):
        """
            List DataSets

            >>> l = domo.ds_list(df_output=True)
            >>> print(l.head())

            :Parameters:
            - `df_output`:  should the result be a dataframe. Default True (Boolean)
            - `per_page`:   results per page. Default 50 (int)
            - `offset`:     offset if you need to paginate results. Default 0 (int)
            - `limit`:      max ouput to return. If 0 then return all results on page. Default 0 (int)

            :Returns:
            list or pandas dataframe depending on parameters

        """
        datasources = self.datasets.list(per_page=per_page,
                                         offset=offset,
                                         limit=limit,
                                         name_like=name_like)
        if df_output == False:
            out = list(datasources)
        else:
            out = DataFrame(list(datasources))
        return out

    def ds_query(self, dataset_id, query, return_data=True):
        """
            Evaluate query and return dataset in a dataframe

            >>> query = {"sql": "SELECT * FROM table LIMIT 2"}
            >>> ds = domo.ds_query('80268aef-e6a1-44f6-a84c-f849d9db05fb', query)
            >>> print(ds.head())

            :Parameters:
            - `dataset_id`:     id of a dataset (str)
            - `query`:          query object (dict)
            - `return_data`:    should the result be a dataframe. Default True (Boolean)

            :Returns:
            dict or pandas dataframe depending on parameters
        """
        output = self.datasets.query(dataset_id, query)
        if(return_data == True):
            output = DataFrame(output['rows'], columns = output['columns'])
        return output


    def ds_get(self, dataset_id, **kwargs):
        """
            Export data to pandas Dataframe

            >>> df = domo.ds_get('80268aef-e6a1-44f6-a84c-f849d9db05fb')
            >>> print(df.head())

            :Parameters:
            - `dataset_id`:     id of a dataset (str)
            - `**kwargs`:       additional keyword arguments to be passed to read_csv


            :Returns:
            pandas dataframe
        """
        csv_download = self.datasets.data_export(dataset_id, include_csv_header=True)

        content = StringIO(csv_download)
        df = read_csv(content, **kwargs)

        # Convert to dates or datetimes if possible
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = to_datetime(df[col])
                except ValueError:
                    pass
                except TypeError:
                    pass

        return df
    
    def ds_get_dict(self,ds_id):
        my_data = self.datasets.data_export(ds_id,True)
        dr = csv.DictReader(StringIO(my_data))
        data_list = list(dr)
        return(data_list)

    def ds_create(self, df_up, name, description='',
                  update_method='REPLACE', key_column_names=[]):
        new_stream = self.utilities.stream_create(df_up,
                                                  name,
                                                  description,
                                                  update_method,
                                                  key_column_names)
        if "dataSet" in new_stream:
            ds_id = new_stream['dataSet']['id']
            self.utilities.stream_upload(ds_id, df_up,
                                         warn_schema_change=False)
            return ds_id
        else:
            raise Exception(("Stream creation didn't work as expected. "
                             "Response: {}").format(new_stream))

    def ds_update(self, ds_id, df_up):
        return self.utilities.stream_upload(ds_id, df_up)

######### PDP #########

    def pdp_create(self, dataset_id, pdp_request):
        """
        Create a PDP policy

        >>> policy = {
          "name": "Only Show Attendees",
          "filters": [ {
            "column": "Attending",
            "values": [ "TRUE" ],
            "operator": "EQUALS"
          } ],
          "users": [ 27 ]
        }
        >>> domo.pdp_create('4405ff58-1957-45f0-82bd-914d989a3ea3', policy)
        {"id" : 8, "type": "user", "name": "Only Show Attendees"
        , "filters": [{"column": "Attending", "values": [ "TRUE" ],   "operator": "EQUALS"
        ,   "not": false } ], "users": [ 27 ],"groups": [ ]}

        :Parameters:
          - `dataset_id`:   id of the dataset PDP will be applied to (String) Required
          Policy Object:
          - `name`: Name of the Policy (String) Required
          - `filters[].column`:	Name of the column to filter on (String) Required
          - `filters[].not`: Determines if NOT is applied to the filter operation (Boolean) Required
          - `filters[].operator`: Matching operator (EQUALS) (String) Required
          - `filters[].values[]`: Values to filter on (String) Required
          - `type`: Type of policy (user or system) (String) Required
          - `users`: List of user IDs the policy applies to (array) Required
          - `groups`: List of group IDs the policy applies to (array) Required
        """
        return self.datasets.create_pdp(dataset_id, pdp_request)

    def pdp_delete(self, dataset_id, policy_id):
        """
        Delete PDP Policy

        >>> domo.pdp_delete('4405ff58-1957-45f0-82bd-914d989a3ea3', 35)

        :Parameters:
        - `dataset_id`: id of the dataset PDP will be applied to (String) Required
        - `policy_id`:  id of the policy to delete (String) Required
        """
        return self.datasets.delete_pdp(dataset_id, policy_id)

    def pdp_list(self, dataset_id, df_output = True):
        """
            List PDP policies

            >>> l = domo.pdp_list(df_output=True)
            >>> print(l.head())

            :Parameters:
            - `dataset_id`:   id of dataset with PDP policies (str) Required
            - `df_output`:  should the result be a dataframe. Default True (Boolean)

            :Returns:
            list or pandas dataframe depending on parameters

        """
        output = self.datasets.list_pdps(dataset_id)
        if(df_output == True):
            output = DataFrame(output)
        return output

    def pdp_update(self, dataset_id, policy_id, policy_update):

        """
        Update a PDP policy

        >>> policy = {
          "name": "Only Show Attendees",
          "filters": [ {
            "column": "Attending",
            "values": [ "TRUE" ],
            "operator": "EQUALS"
          } ],
          "users": [ 27 ]
        }
        >>> domo.pdp_create('4405ff58-1957-45f0-82bd-914d989a3ea3', 4, policy)
        {"id" : 8, "type": "user", "name": "Only Show Attendees"
        , "filters": [{"column": "Attending", "values": [ "TRUE" ],   "operator": "EQUALS"
        ,   "not": false } ], "users": [ 27 ],"groups": [ ]}

        :Parameters:
          - `dataset_id`:   id of the dataset PDP will be applied to (String) Required
          - `policy_id`:    id of the PDP pollicy that will be updated (String) Required
          Policy Object:
          - `name`: Name of the Policy (String) Required
          - `filters[].column`:	Name of the column to filter on (String) Required
          - `filters[].not`: Determines if NOT is applied to the filter operation (Boolean) Required
          - `filters[].operator`: Matching operator (EQUALS) (String) Required
          - `filters[].values[]`: Values to filter on (String) Required
          - `type`: Type of policy (user or system) (String) Required
          - `users`: List of user IDs the policy applies to (array) Required
          - `groups`: List of group IDs the policy applies to (array) Required
        """
        return self.datasets.update_pdp(dataset_id, policy_id, policy_update)


######### Pages #########

    def page_create(self, name, **kwargs):
        """Create a new page.

        >>> page = {'name':'New Page'}
        >>> new_page = domo.pages.create(**page)
        >>> print(new_page)
        {'id': 123456789, 'parentId': 0, 'name': 'My Page',
        'locked': False, 'ownerId': 12345, 'cardIds': [],
        'visibility': {'userIds': 12345}}

        :Parameters:
          - `name`: The name of the new page
          - `parentId`: (optional) If present create page as subpage
          - `locked`: (optional) whether to lock the page
          - `cardIds`: (optional) cards to place on the page
          - `visibility`: (optional) dict of userIds and/or groupIds to
            give access to

        :Returns:
          - A dict representing the page
        """
        return self.pages.create(name, **kwargs)


    def page_get(self, page_id):
        """Get a page.

        >>> page = domo.pages.get(page_id)
        >>> print(page)
        {'id': 123456789, 'parentId': 0, 'name': 'My Page',
        'locked': False, 'ownerId': 12345, 'cardIds': [],
        'visibility': {'userIds': 12345}}

        :Parameters:
          - `page_id`: ID of the page to get

        :returns:
          - A dict representing the page
        """
        return self.pages.get(page_id)


    def page_delete(self, page_id):
        """Delete a page.

        :Parameters:
          - `page_id`: ID of the page to delete
        """
        return self.pages.delete(page_id)


    def collections_create(self, page_id, title, **kwargs):
        """Create a collection on a page.

        >>> collection = domo.pages.create_collection(page_id,
                                                      'Collection')
        >>> print(collection)
        {'id': 1234321, 'title': 'Collection', 'description': '',
        'cardIds': []}

        :Parameters:
          - `page_id`: ID of the page to create a collection on
          - `title`: The title of the collection
          - `description`: (optional) The description of the collection
          - `cardIds`: (optional) cards to place in the collection

        :Returns:
          - A dict representing the collection
        """
        return self.pages.create_collection(page_id, title, **kwargs)


    def page_get_collections(self, page_id):
        """Get a collections of a page

        >>> print(domo.pages.get_collections(page_id))
        [{'id': 1234321, 'title': 'Collection', 'description': '',
        'cardIds': []}]

        :Parameters:
          - `page_id`: ID of the page

        :Returns:
          - A list of dicts representing the collections
        """
        return self.pages.get_collections(page_id)


    def collections_update(self, page_id, collection_id=None, **kwargs):
        """Update a collection of a page.

        >>> collections = domo.pages.get_collections(page_id)
        >>> print(collections)
        [{'id': 1234321, 'title': 'Collection', 'description': '',
        'cardIds': []}]
        >>> collection_id = collections[0]['id']
        >>> domo.pages.update_collection(page_id, collection_id,
                                         description='description',
                                         cardIds=[54321, 13579])
        >>> print(domo.pages.get_collections(page_id))
        [{'id': 1234321, 'title': 'Collection',
        'description': 'description', 'cardIds': [54321, 13579]}]

        # Using **kwargs:
        >>> collections = domo.pages.get_collections(page_id)
        >>> collections[0]['description'] = 'Description'
        >>> domo.pages.update_collection(page_id, **collections[0])

        :Parameters:
          - `page_id`: ID of the page the collection is on
          - `collection_id`: ID of the collection. Can also be provided
            by supplying `id` to **kwargs. This allows for calling
            get_collections, updating one of the returned collections,
            then passing it to update_collection.
          - `title`: (optional) update the title
          - `description`: (optional) update the description
          - `cardIds`: (optional) update cards in the collection

        :Returns:
          - A dict representing the collection
        """
        return self.pages.update_collection(page_id, collection_id, **kwargs)


    def collections_delete(self, page_id, collection_id):
        """Delete a collection from a page.

        :Parameters:
          - `page_id`: ID of the page the collection is on
          - `collection_id`: ID of the collection to delete
        """
        return self.pages.delete_collection(page_id, collection_id)


    def page_list(self, per_page=50, offset=0, limit=0):
        """List pages.
        Returns a list of dicts (with nesting possible)
        If limit is supplied and non-zero, returns up to limit pages
        """
        return list(self.pages.list())


    def page_update(self, page_id=None, **kwargs):
        """Update a page.

        >>> print(domo.pages.get(page_id))
        {'id': 123456789, 'parentId': 0, 'name': 'My Page',
        'locked': False, 'ownerId': 12345, 'cardIds': [],
        'visibility': {'userIds': 12345}}
        >>> domo.pages.update(page_id, locked=True,
                              cardIds=[54321, 13579])
        >>> print(domo.pages.get(page_id))
        {'id': 123456789, 'parentId': 0, 'name': 'My Page',
        'locked': True, 'ownerId': 12345, 'cardIds': [54321, 13579],
        'visibility': {'userIds': 12345}}

        # Using **kwargs:
        >>> page = domo.pages.get(page_id)
        >>> page['cardIds'].append(new_card_id)
        >>> domo.pages.update(**page)

        :Parameters:
          - `page_id`: ID of the page to update. Can also be provided
            by supplying `id` to **kwargs. This allows for calling get,
            updating the returned object, then passing it to update.
          - `name`: (optional) rename the page
          - `parentId`: (optional) turn page into subpage, or subpage
            into top-level page if parentId is present and falsey
          - `ownerId`: (optional) change owner of the page
          - `locked`: (optional) lock or unlock the page
          - `collectionIds`: (optional) reorder collections on page
          - `cardIds`: (optional) specify which cards to have on page
          - `visibility`: (optional) change who can see the page
        """
        return self.pages.update(page_id, **kwargs)


######### Groups #########

    def groups_add_users(self, group_id, user_id):
        """
            Add a User to a Group
        """

        if isinstance(user_id,list):
            for x in user_id:
                self.groups.add_user(group_id, x)
        else:
            self.groups.add_user(group_id, user_id)

        return 'success'



    def groups_create(self, group_name, users=-1, active='true'):
        """
            Create a Group
        """
        req_body = {'name':group_name,'active':active}
        grp_created = self.groups.create(req_body)
        if (not isinstance(users,list) and users > 0) or isinstance(users,list):
            self.groups_add_users(grp_created['id'],users)

        return grp_created



    def groups_delete(self, group_id):
        """
            Delete a Group
        """
        existing_users = self.groups_list_users(group_id)
        self.groups_remove_users(group_id,existing_users)
        return self.groups.delete(group_id)



    def groups_get(self, group_id):
        """
            Get a Group Definition
        """
        return self.groups.get(group_id)



    def groups_list(self):
        """
            List all groups in Domo instance in a pandas dataframe.
        """
        grps = []
        n_ret = 1
        off = 0
        batch_size = 500
        while n_ret > 0:
            gg = self.groups.list(batch_size,off*batch_size)
            grps.extend(gg)
            n_ret = gg.__len__()
            off += 1
        return DataFrame(grps)


    def groups_list_users(self, group_id):
        """
            List Users in a Group
        """
        user_list = []
        n_ret = 1
        off = 0
        batch_size=500
        while n_ret > 0:
            i_users = self.groups.list_users(group_id,limit=batch_size,offset=off*batch_size)
            user_list.extend(i_users)
            n_ret = i_users.__len__()
            off += 1

        return user_list



    def groups_remove_users(self, group_id, user_id):
        """
            Remove a User to a Group
        """
        if isinstance(user_id,list):
            for x in user_id:
                self.groups.remove_user(group_id, x)
        else:
            self.groups.remove_user(group_id, user_id)

        return 'success'


######### Accounts #########
    def accounts_list(self):
        """List accounts.
        Returns a generator that will call the API multiple times
        If limit is supplied and non-zero, returns up to limit accounts

        >>> list(domo.accounts.list())
        [{'id': '40', 'name': 'DataSet Copy Test', ...},
        {'id': '41', 'name': 'DataSet Copy Test2', ...}]

        :Parameters:
        - `per_page`:   results per page. Default 50 (int)
        - `offset`:     offset if you need to paginate results. Default 0 (int)
        - `limit`:      max ouput to return. If 0 then return all results on page. Default 0 (int)


        :returns:
          - A list of dicts (with nesting possible)
        """
        return list(self.accounts.list())

    def accounts_get(self, account_id):
        """Get a account.

        >>> account = domo.accounts.get(account_id)
        >>> print(account)
        {'id': '40', 'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}

        :Parameters:
          - `account_id`: ID of the account to get (str)

        :returns:
          - A dict representing the account
        """
        return self.accounts.get(account_id)

    def accounts_delete(self, account_id):
        """Delete a account.

        :Parameters:
          - `account_id`: ID of the account to delete
        """
        return self.accounts.delete(account_id)

    def accounts_create(self, **kwargs):
        """Create a new account.

        >>> account = { 'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}
        >>> new_account = domo.accounts.create(**account)
        >>> print(new_account)
        {'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}


        :Returns:
          - A dict representing the account
        """
        return self.accounts.create(**kwargs)

    def accounts_update(self, account_id, **kwargs):
        """Update a account.

        >>> print(domo.accounts.get(account_id))
        {'id': '40', 'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}
        updatedAccount = {'name': 'DataSet Copy Test2, 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}
        >>> domo.accounts.update(account_id, **updatedAccount)
        >>> print(domo.accounts.get(account_id))
        {'id': '40', 'name': 'DataSet Copy Test2, 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}


        :Parameters:
          - `account_id`: ID of the account to update.
          - `kwargs`: New account object
        """
        return self.accounts.update(account_id, **kwargs)

######### Users #########
    def users_add(self, x_name, x_email, x_role, x_sendInvite=False):
        uu = CreateUserRequest()
        uu.name = x_name
        uu.email = x_email
        uu.role = x_role
        return self.users.create(uu,x_sendInvite)

    def users_get(self, user_id):
        return self.users.get(user_id)

    def users_list(self,df_output=True):
        return self.users.list_all(df_output)

    def users_update(self, user_id, user_def):
        return self.users.update(user_id, user_def)

    def users_delete(self, user_id):
        return self.users.delete(user_id)
