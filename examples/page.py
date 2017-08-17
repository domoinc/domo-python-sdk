

def pages(domo):
    '''Page Docs: https://developer.domo.com/docs/domo-apis/pages
    '''
    domo.logger.info("\n**** Domo API - Page Examples ****\n")

    # Create a page
    page = domo.pages.create('New Page')
    domo.logger.info("Created Page {}".format(page['id']))

    # Create a subpage
    subpage = domo.pages.create('Sub Page', parentId=page['id'])
    domo.logger.info("Created Subpage {}".format(subpage['id']))

    # Update the page using returned page
    page['name'] = 'Updated Page'
    domo.pages.update(**page)
    domo.logger.info("Renamed Page {}".format(page['id']))

    # Turn subpage into to top-level page using keyword argument
    domo.pages.update(subpage['id'], parentId=None)
    domo.logger.info("Moved Page to top level {}".format(subpage['id']))

    # Get the page
    page = domo.pages.get(page['id'])

    # List pages
    page_list = list(domo.pages.list())
    domo.logger.info("Retrieved a list of {} top-level page(s)".format(
                                                               len(page_list)))

    # Create a few collections
    collections = [
        domo.pages.create_collection(page['id'], 'First Collection'),
        domo.pages.create_collection(page['id'], 'Second Collection'),
    ]
    domo.logger.info("Created two collections on page {}".format(page['id']))

    # Get collections
    collection_list = domo.pages.get_collections(page['id'])
    domo.logger.info("Retrieved a list of {} collections".format(
                                                         len(collection_list)))

    # Update collection
    collections[1]['title'] = 'Last Collection'
    domo.pages.update_collection(page['id'], **collections[1])
    domo.logger.info("Updated collection {}: {}".format(collections[1]['id'],
                                                     collections[1]['title']))

    # Clean up
    for collection in collections:
        domo.pages.delete_collection(page['id'], collection['id'])
    domo.pages.delete(page['id'])
    domo.pages.delete(subpage['id'])
    domo.logger.info("Deleted collections and pages")
