from collective.plonetruegallery.settings import ANNOTATION_KEY
from collective.plonetruegallery.settings import GallerySettings
from zope.annotation.interfaces import IAnnotations

import json


SETTINGS_FILENAME = 'gallerysettings.json'


def install(context):
    if not context.readDataFile('collective.plonetruegallery.txt'):
        return
    site = context.getSite()
    default_settings = context.readDataFile(SETTINGS_FILENAME)
    if default_settings:
        default_settings = json.loads(default_settings)
        settings = GallerySettings(site)
        for key, value in default_settings.items():
            setattr(settings, key, value)


def export(context):
    site = context.getSite()
    annotations = IAnnotations(site)

    settings = annotations.get(ANNOTATION_KEY, None)
    if settings is not None:
        context.writeDataFile(
            SETTINGS_FILENAME,
            json.dumps(dict(settings), indent=4),
            'application/json',
        )
