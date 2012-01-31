from Products.CMFCore.utils import getToolByName


def install(context):

    if not context.readDataFile('collective.plonetruegallery.txt'):
        return

    site = context.getSite()
    types = getToolByName(site, 'portal_types')
    if 'Large Plone Folder' in types.objectIds():
        folder = types['Large Plone Folder']
        view_methods = set(folder.view_methods)
        view_methods.add('galleryview')
        folder.view_methods = tuple(view_methods)


def uninstall(context):
    if not context.readDataFile('collective.plonetruegallery.uninstall.txt'):
        return

    portal = context.getSite()
    portal_actions = getToolByName(portal, 'portal_actions')
    object_buttons = portal_actions.object

    actions_to_remove = ('gallery_settings', 'refresh-gallery')
    for action in actions_to_remove:
        if action in object_buttons.objectIds():
            object_buttons.manage_delObjects([action])

    #remove view
    types_to_remove = ('Large Plone Folder', 'Folder', 'Topic')
    types = getToolByName(portal, 'portal_types')

    for _type in types_to_remove:
        if _type in types.objectIds():
            folder = types[_type]
            view_methods = list(folder.view_methods)
            view_methods.remove('galleryview')
            folder.view_methods = tuple(view_methods)
