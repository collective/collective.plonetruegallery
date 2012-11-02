from Products.CMFCore.utils import getToolByName
import json
from collective.plonetruegallery.settings import GallerySettings
from collective.plonetruegallery.settings import ANNOTATION_KEY
from zope.annotation.interfaces import IAnnotations


SETTINGS_FILENAME = 'gallerysettings.json'


def install(context):
    site = context.getSite()
    default_settings = context.readDataFile(SETTINGS_FILENAME)
    if default_settings:
        default_settings = json.loads(default_settings)
        settings = GallerySettings(site)
        for key, value in default_settings.items():
            setattr(settings, key, value)

    if not context.readDataFile('collective.plonetruegallery.txt'):
        return

    types = getToolByName(site, 'portal_types')
    if 'Large Plone Folder' in types.objectIds():
        folder = types['Large Plone Folder']
        view_methods = set(folder.view_methods)
        view_methods.add('galleryview')
        folder.view_methods = tuple(view_methods)
    if 'Collection' in types.objectIds():
        folder = types['Collection']
        view_methods = set(folder.view_methods)
        view_methods.add('galleryview')
        folder.view_methods = tuple(view_methods)


def export(context):
    site = context.getSite()
    annotations = IAnnotations(site)

    settings = annotations.get(ANNOTATION_KEY, None)
    if settings is not None:
        context.writeDataFile(SETTINGS_FILENAME,
                              json.dumps(dict(settings), indent=4),
                              'application/json')


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
    types_to_remove = ('Large Plone Folder', 'Folder', 'Topic', 'Collection')
    types = getToolByName(portal, 'portal_types')

    for _type in types_to_remove:
        if _type in types.objectIds():
            folder = types[_type]
            view_methods = list(folder.view_methods)
            view_methods.remove('galleryview')
            folder.view_methods = tuple(view_methods)
