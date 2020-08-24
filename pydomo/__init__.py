from pydomo.Transport import DomoAPITransport
from pydomo.datasets import DataSetClient
from pydomo.groups import GroupClient
from pydomo.pages import PageClient
from pydomo.streams import StreamClient
from pydomo.users import UserClient
from pydomo.accounts import AccountClient
from pandas import read_csv
from pandas import DataFrame
from io import StringIO
import logging

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

        if kwargs.get('log_level'):
            self.logger.setLevel(kwargs['log_level'])
        self.logger.debug("\n" + DOMO + "\n")

        self.transport = DomoAPITransport(client_id, client_secret, api_host, kwargs.get('use_https', True), self.logger)
        self.datasets = DataSetClient(self.transport, self.logger)
        self.groups = GroupClient(self.transport, self.logger)
        self.pages = PageClient(self.transport, self.logger)
        self.streams = StreamClient(self.transport, self.logger)
        self.users = UserClient(self.transport, self.logger)

    ## Dataset functions for similar syntax and return datastructures as the rDomo package
    def ds_meta(self, dataset_id):
        """
            Get a DataSet metadata
        """
        return self.datasets.get(dataset_id)

    def ds_delete(self, dataset_id):
        """
            Delete a DataSet naming convention equivilent with rDomo
        """
        return self.datasets.delete(dataset_id)

    def ds_list(self, per_page=50, offset=0, limit=0, df_output = True):
        """
            List DataSets
            Returns either a list or dataframe with metadata of datasets
            If limit is supplied and non-zero, returns up to limit datasets
        """
        l = self.datasets.list(per_page=50, offset=0, limit=0)
        if df_output == False:
            out = list(l)
        else:
            out = DataFrame(list(l))
        return out
    
    def ds_query(self, dataset_id, query, return_data=True):
        """
            Evaluate query and return dataset in a dataframe
            By default this will return a pandas dataframe. If return_data is set to false function will return a json object
        """
        output = self.datasets.query(dataset_id, query)
        if(return_data == True):
            output = DataFrame(output['rows'], columns = output['columns'])
        return output


    def ds_get(self, dataset_id, include_csv_header=True):
        """
            Export data to pandas Dataframe
        """    
        csv_download = self.datasets.data_export(dataset_id, include_csv_header)

        content = StringIO(csv_download)
        df = read_csv(content)
        return df

    ## PDP

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
          - `dataset_id`: String Required  Id of the dataset PDP will be applied to
          Policy Object:
          - `name`:	String	Required	Name of the Policy
          - `filters[].column`:	String	Required	Name of the column to filter on
          - `filters[].not`:	Boolean	Required	Determines if NOT is applied to the filter operation
          - `filters[].operator`:	String	Required	Matching operator (EQUALS)
          - `filters[].values[]`:	String	Required	Values to filter on
          - `type`:	String	Required	Type of policy (user or system)
          - `users`:	Array	Required	List of user IDs the policy applies to
          - `groups`:	Array	Required	List of group IDs the policy applies to
        """
        return self.datasets.create_pdp(dataset_id, pdp_request)

    def pdp_delete(self, dataset_id, policy_id):
        return self.datasets.delete_pdp(dataset_id, policy_id)

    def pdp_list(self, dataset_id):
        return self.datasets.list_pdps(dataset_id)

    def pdp_update(self, dataset_id, policy_id, policy_update):
        return self.datasets.update_pdp(dataset_id, policy_id, policy_update)


    ## Pages

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
        return self.delete_collection(page_id, collection_id)


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


    ## Groups

    def groups_add_users(self, group_id, user_id):
        """
            Add a User to a Group
        """
        return self.groups.add_user(group_id, user_id)



    def groups_create(self, group_request):
        """
            Create a Group
        """
        return self.groups.create(group_request)



    def groups_delete(self, group_id):
        """
            Delete a Group
        """
        return self.groups.delete(group_id)



    def groups_get(self, group_id):
        """
            Get a Group Definition
        """
        return self.groups.get(group_id)



    def groups_list(self, limit=1000, offset=0):
        """
            List all groups in Domo instance in a pandas dataframe.
        """
        return pd.DataFrame(self.groups.list(limit, offset))



    def groups_list_users(self, group_id, limit=1000, offset=0):
        """
            List Users in a Group
        """
        return self.groups.list_users(group_id, limit, offset)



    def groups_remove_users(self, group_id, user_id):
        """
            Remove a User to a Group
        """
        return self.groups.remove_user(group_id, user_id)



