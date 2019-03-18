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
try:
    from plone.uuid.interfaces import IUUID
except:
    def IUUID(_, _2=None):
        return None


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
        uid = IUUID(self.gallery, None)
        if uid is None:
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

    def get_first_image(self):
        if len(self.cooked_images) > 0:
            return self.cooked_images[0]
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


class ImageInfo(object):

    def __init__(self, brain, info_retriever):
        self.brain = brain
        self.info_retriever = info_retriever
        self.gallery_adapter = self.info_retriever.gallery_adapter
        self._obj = None
        self.base_url = self.brain.getURL()
        self.portal_type = brain.portal_type
        self.enable_bodytext = self.gallery_adapter.settings.enable_bodytext

    @property
    def obj(self):
        if self._obj is None:
            self._obj = self.brain.getObject()
        return self._obj

    @property
    def image_url(self):
        scale = self.gallery_adapter.size_map[self.gallery_adapter.settings.size]
        return "%s/@@images/image/%s" % (self.base_url, scale)

    @property
    def thumb_url(self):
        base_url = self.base_url
        if self.portal_type in ('GalleryImage',):
            field = self.obj.getField('thumbnailImage')
            if field:
                if field.get_size(self.obj) > 0:
                    return '%s/@@thumbnailImage' % base_url
        gallery_thumbnail_size = self.gallery_adapter.settings.thumb_size
        if not gallery_thumbnail_size:
            gallery_thumbnail_size = 'tile'
        return "%s/@@images/image/%s" % (base_url, gallery_thumbnail_size)

    @property
    def link_url(self):
        if self.enable_bodytext and self.portal_type in ('GalleryImage',):
            field = self.obj.getField('linksTo')
            if field:
                val = field.get(self.obj)
                if val:
                    return val.absolute_url()
        return self.base_url

    @property
    def copyright(self):
        if self.gallery_adapter.settings.copyright:
            if hasattr(self.obj, 'Rights') and callable(self.obj.Rights):
                copyright = self.obj.Rights()
                if copyright:
                    return copyright
        return ""
        
    @property
    def bodytext(self):
        if self.enable_bodytext:
            if self.portal_type in ('News Item', 'GalleryImage'):
                field = self.obj.getField('text')
                if field:
                    return field.getRaw(self.obj)
        return ""

    @property
    def download_url(self):
        return self.base_url + '/at_download/image'

    @property
    def original_image_url(self):
        return self.base_url + '/image'


class BaseImageInformationRetriever(object):

    def __init__(self, context, gallery_adapter):
        self.pm = getToolByName(context, 'portal_membership')
        self.context = context
        self.gallery_adapter = gallery_adapter

    def assemble_image_information(self, image):
        info = ImageInfo(image, self)
        return {
            'image_url': info.image_url,
            'thumb_url': info.thumb_url,
            'original_image_url': info.original_image_url,
            'download_url': info.download_url,
            'link': info.link_url,
            'title': image.Title,
            'description': image.Description,
            'copyright':   info.copyright,
            'portal_type': image.portal_type,
            'keywords':  ' '.join(image.Subject),
            'bodytext': info.bodytext
        }
