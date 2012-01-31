from zope.interface import implements
from zope.component import getUtilitiesFor
from zope.component import getUtility
from collective.plonetruegallery.interfaces import IDisplayType
from zope.component import getMultiAdapter
from settings import GallerySettings
from interfaces import IGallerySettings
from collective.plonetruegallery.config import named_adapter_prefix
from collective.plonetruegallery.config import DISPLAY_NAME_VIEW_PREFIX
from vocabularies import GalleryTypeVocabulary, DisplayTypeVocabulary


def getGalleryAdapter(gallery, request, gallery_type=None):
    if gallery_type is None:
        gallery_type = GallerySettings(gallery).gallery_type

    possible_types = GalleryTypeVocabulary(gallery)
    if gallery_type not in possible_types.by_value.keys():
        gallery_type = IGallerySettings['gallery_type'].default

    return getMultiAdapter(
        (gallery, request),
        name=named_adapter_prefix + gallery_type
    )


def getDisplayAdapter(adapter, display_type=None):
    if display_type is None:
        display_type = GallerySettings(adapter.gallery).display_type

    possible_types = DisplayTypeVocabulary(adapter.gallery)
    if display_type not in possible_types.by_value.keys():
        display_type = IGallerySettings['display_type'].default

    return getMultiAdapter(
        (adapter.gallery, adapter.request),
        name=DISPLAY_NAME_VIEW_PREFIX + display_type
    )


def getDisplayType(name):
    return getUtility(IDisplayType, name=DISPLAY_NAME_VIEW_PREFIX + name)


def getAllDisplayTypes():
    utils = list(getUtilitiesFor(IDisplayType))
    utils = sorted(utils, key=lambda x: x[1].name)
    return [utility for name, utility in utils]


def createSettingsFactory(schema):
    class Settings(GallerySettings):
        implements(schema)

        def __init__(self, context, interfaces=[schema]):
            super(Settings, self).__init__(context, interfaces)

    return Settings
