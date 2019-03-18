from collective.plonetruegallery.interfaces import IDisplayType
from collective.plonetruegallery.interfaces import IBatchingDisplayType
from plone.memoize.view import memoize
from zope.interface import implements
from collective.plonetruegallery.settings import GallerySettings
from Products.CMFPlone.PloneBatch import Batch
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from collective.plonetruegallery.utils import getGalleryAdapter


def jsbool(val):
    return str(val).lower()


class BaseDisplayType(BrowserView):
    implements(IDisplayType)

    name = None
    description = None
    schema = None
    userWarning = None
    staticFilesRelative = '++resource++plonetruegallery.resources'
    typeStaticFilesRelative = ''

    def __init__(self, context, request):
        super(BaseDisplayType, self).__init__(context, request)
        self.adapter = getGalleryAdapter(context, request)
        self.context = self.gallery = self.adapter.gallery
        self.settings = GallerySettings(context,
                            interfaces=[self.adapter.schema, self.schema])
        portal_state = getMultiAdapter((context, request),
                                        name='plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.staticFiles = "%s/%s" % (self.portal_url,
                                      self.staticFilesRelative)
        self.typeStaticFiles = '%s/%s' % (self.portal_url,
                                          self.typeStaticFilesRelative)

    def content(self):
        return self.index()

    @property
    def height(self):
        return self.adapter.sizes[self.settings.size]['height']

    @property
    def width(self):
        return self.adapter.sizes[self.settings.size]['width']

    @memoize
    def get_start_image_index(self):
        if 'start_image' in self.request:
            si = self.request.get('start_image', '')
            images = self.adapter.cooked_images
            for index in range(0, len(images)):
                if si == images[index]['title']:
                    return index
        return 0

    start_image_index = property(get_start_image_index)

    def css(self):
        return ''

    def javascript(self):
        return ''


class BatchingDisplayType(BaseDisplayType):
    implements(IDisplayType, IBatchingDisplayType)

    @memoize
    def uses_start_image(self):
        """
        disable start image if a batch start is specified.
        """
        return bool('start_image' in self.request) and \
            not bool('b_start' in self.request)

    @memoize
    def get_b_start(self):
        if self.uses_start_image():
            page = self.get_page()
            return page * self.settings.batch_size
        else:
            return int(self.request.get('b_start', 0))

    b_start = property(get_b_start)

    @memoize
    def get_start_image_index(self):
        if self.uses_start_image():
            index = super(BatchingDisplayType, self).get_start_image_index()
            return index - (self.get_page() * self.settings.batch_size)
        else:
            return 0

    start_image_index = property(get_start_image_index)

    @memoize
    def get_page(self):
        index = super(BatchingDisplayType, self).get_start_image_index()
        return index / self.settings.batch_size

    @property
    @memoize
    def start_automatically(self):
        return self.uses_start_image() or \
            self.adapter.number_of_images < self.settings.batch_size

    @property
    @memoize
    def batch(self):
        return Batch(self.adapter.cooked_images, self.settings.batch_size,
                                              int(self.b_start), orphan=1)
