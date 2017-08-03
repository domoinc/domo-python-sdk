import requests

from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod

PAGE_DESC = "Page"
COLLECTION_DESC = "Collection"
URL_BASE = '/v1/pages'

PAGE_CREATION_KWARGS = [
    'parentId',
    'locked',
    'cardIds',
    'visibility'
]

PAGE_UPDATE_KWARGS = [
    'id',
    'name',
    'parentId',
    'ownerId',
    'locked',
    'collectionIds',
    'cardIds',
    'visibility'
]

COLLECTION_CREATION_KWARGS = [
    'description',
    'cardIds'
]

COLLECTION_UPDATE_KWARGS = [
    'id',
    'description',
    'cardIds',
    'title'
]


class PageClient(DomoAPIClient):
    """
        Pages
        - Programmatically manage Domo Pages
        - Docs: https://developer.domo.com/docs/data-apis/pages
    """

    def create(self, name, **kwargs):
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

        self._validate_params(kwargs, PAGE_CREATION_KWARGS)

        page_request = {'name': name}
        page_request.update(kwargs)
        return self._create(URL_BASE, page_request, {}, PAGE_DESC)

    def get(self, page_id):
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
        url = '{base}/{page_id}'.format(base=URL_BASE, page_id=page_id)
        return self._get(url, PAGE_DESC)

    def list(self):
        """List pages.

        >>> domo.pages.list()
        [{'id': 123456789, 'name': 'My Page', 'children': []}, ...]

        :returns:
          - A list of dicts (with nesting possible)
        """
        return self._list(URL_BASE, {}, PAGE_DESC)

    def update(self, page_id=None, **kwargs):
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
            into top-level page if parentId is 0
          - `ownerId`: (optional) change owner of the page
          - `locked`: (optional) lock or unlock the page
          - `collectionIds`: (optional) reorder collections on page
          - `cardIds`: (optional) specify which cards to have on page
          - `visibility`: (optional) change who can see the page
        """

        self._validate_params(kwargs, PAGE_UPDATE_KWARGS)
        if page_id is None and 'id' not in kwargs:
            raise TypeError("update() missing required argument: 'page_id'")
        elif 'id' in kwargs:
            if page_id is not None and page_id != kwargs['id']:
                raise ValueError('ambiguous page ID - page_id and id both '
                                 'supplied but do not match')
            page_id = kwargs['id']
            del kwargs['id']

        url = '{base}/{page_id}'.format(base=URL_BASE, page_id=page_id)
        return self._update(url,
                            HTTPMethod.PUT,
                            requests.codes.NO_CONTENT,
                            kwargs,
                            PAGE_DESC)

    def delete(self, page_id):
        """Delete a page.

        :Parameters:
          - `page_id`: ID of the page to delete
        """
        url = '{base}/{page_id}'.format(base=URL_BASE, page_id=page_id)
        return self._delete(url, PAGE_DESC)

    def create_collection(self, page_id, title, **kwargs):
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

        self._validate_params(kwargs, COLLECTION_CREATION_KWARGS)
        collection_request = {'title': title}
        collection_request.update(kwargs)

        url = '{base}/{page_id}/collections'.format(
                base=URL_BASE, page_id=page_id)
        return self._create(url, collection_request, {}, COLLECTION_DESC)

    def get_collections(self, page_id):
        """Get a collections of a page

        >>> print(domo.pages.get_collections(page_id))
        [{'id': 1234321, 'title': 'Collection', 'description': '',
        'cardIds': []}]

        :Parameters:
          - `page_id`: ID of the page

        :Returns:
          - A list of dicts representing the collections
        """
        url = '{base}/{page_id}/collections'.format(base=URL_BASE,
                                                    page_id=page_id)
        return self._get(url, COLLECTION_DESC)

    def update_collection(self, page_id, collection_id=None, **kwargs):
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

        self._validate_params(kwargs, COLLECTION_UPDATE_KWARGS)
        if collection_id is None and 'id' not in kwargs:
            raise TypeError("update() missing required argument: "
                            "'collection_id'")
        elif 'id' in kwargs:
            if collection_id is not None and collection_id != kwargs['id']:
                raise ValueError('ambiguous collection ID - collection_id and'
                                 ' id both supplied but do not match')
            collection_id = kwargs['id']
            del kwargs['id']

        url = '{base}/{page_id}/collections/{collection_id}'.format(
                base=URL_BASE, page_id=page_id, collection_id=collection_id)
        return self._update(url,
                            HTTPMethod.PUT,
                            requests.codes.NO_CONTENT,
                            kwargs,
                            COLLECTION_DESC)

    def delete_collection(self, page_id, collection_id):
        """Delete a collection from a page.

        :Parameters:
          - `page_id`: ID of the page the collection is on
          - `collection_id`: ID of the collection to delete
        """
        url = '{base}/{page_id}/collections/{collection_id}'.format(
                base=URL_BASE, page_id=page_id, collection_id=collection_id)
        return self._delete(url, COLLECTION_DESC)
