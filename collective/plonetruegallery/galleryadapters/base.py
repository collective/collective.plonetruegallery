import time
import random

from collective.plonetruegallery import PTGMessageFactory as _
from collective.plonetruegallery.interfaces import IGalleryAdapter, IGallery
from collective.plonetruegallery.settings import GallerySettings

from zLOG import LOG, INFO

from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize


class BaseAdapter(object):

    implements(IGalleryAdapter)
    adapts(IGallery, IDefaultBrowserLayer)

    sizes = {}
    settings = None
    schema = None
    name = u"base"
    description = _(u"label_base_gallery_type",
        default=u"base: this isn't actually a gallery type.  "
                u"Think abstract class here...")

    cook_delay = 24 * 60 * 60  # will update once a day

    def __init__(self, gallery, request):
        self.gallery = gallery
        self.request = request
        self.settings = GallerySettings(self.gallery, interfaces=[self.schema])

        if self.time_to_cook():
            self.cook()

    @property
    @memoize
    def subgalleries(self):
        return self.get_subgalleries()

    def get_subgalleries(self, **kwargs):
        catalog = getToolByName(self.gallery, 'portal_catalog')
        gallery_path = self.gallery.getPhysicalPath()
        results = catalog.searchResults(
            path='/'.join(gallery_path),
            object_provides=IGallery.__identifier__,
            **kwargs
        )
        uid = self.gallery.UID()

        def afilter(i):
            """prevent same object and multiple nested galleries"""
            return i.UID != uid and \
                len(i.getPath().split('/')) == len(gallery_path) + 1 and \
                getMultiAdapter(
                    (i.getObject(), self.request),
                    name='plonetruegallery_util'
                ).enabled()

        return filter(afilter, results)

    @property
    def contains_sub_galleries(self):
        return len(self.subgalleries) > 0

    def time_to_cook(self):
        return (self.settings.last_cooked_time_in_seconds + self.cook_delay) \
            <= (time.time())

    def log_error(self, ex='', inst='', msg=""):
        LOG('collective.plonetruegallery', INFO,
            "%s adapter, gallery is %s\n%s\n%s\n%s" %
            (self.name, str(self.gallery), msg, ex, inst))

    def cook(self):
        self.settings.cooked_images = self.retrieve_images()
        self.settings.last_cooked_time_in_seconds = time.time()

    def get_random_image(self):
        if len(self.cooked_images) > 0:
            return self.cooked_images[random.randint(0,
                self.number_of_images - 1)]
        else:
            return {}

    @property
    def number_of_images(self):
        return len(self.cooked_images)

    def retrieve_images(self):
        raise Exception("Not implemented")

    @property
    def cooked_images(self):
        return self.settings.cooked_images


class BaseImageInformationRetriever(object):

    def __init__(self, context, gallery_adapter):
        self.pm = getToolByName(context, 'portal_membership')
        self.context = context
        self.gallery_adapter = gallery_adapter

    def assemble_image_information(self, image):
        return {
            'image_url': self.get_image_url(image),
            'thumb_url': self.get_thumb_url(image),
            'link': self.get_link_url(image),
            'title': image.Title,
            'description': image.Description
        }

    def get_link_url(self, image):
        return image.getURL()

    def get_image_url(self, image):
        return "%s/image_%s" % (
                image.getURL(), self.
                gallery_adapter.size_map[self.gallery_adapter.settings.size])

    def get_thumb_url(self, image):
        gallery_thumbnail_size = self.gallery_adapter.settings.thumb_size
        if not gallery_thumbnail_size:
            gallery_thumbnail_size = 'tile'
        return "%s/image_%s" % (image.getURL(), gallery_thumbnail_size)
