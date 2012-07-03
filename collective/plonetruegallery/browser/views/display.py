from collective.plonetruegallery.interfaces import IDisplayType
from collective.plonetruegallery.interfaces import IBatchingDisplayType
from collective.plonetruegallery.interfaces import \
    IThumbnailzoomDisplaySettings
from plone.memoize.view import memoize
from zope.interface import implements
from collective.plonetruegallery import PTGMessageFactory as _
from collective.plonetruegallery.settings import GallerySettings
from Products.CMFPlone.PloneBatch import Batch
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.utils import createSettingsFactory


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


class ThumbnailzoomDisplayType(BatchingDisplayType):
    name = u"thumbnailzoom"
    schema = IThumbnailzoomDisplaySettings
    description = _(u"label_thumbnailzoom_display_type",
        default=u"Thumbnailzoom")

    def javascript(self):
        return u"""
<script type="text/javascript" charset="utf-8">
$(window).load(function(){
    //set and get some variables
    var thumbnail = {
        imgIncrease : %(increase)i,
        effectDuration : %(effectduration)i,
        imgWidth : $('.thumbnailWrapper ul li').find('img').width(),
        imgHeight : $('.thumbnailWrapper ul li').find('img').height()
    };

    //make the list items same size as the images
    $('.thumbnailWrapper ul li').css({
        'width' : thumbnail.imgWidth,
        'height' : thumbnail.imgHeight
    });

    //when mouse over the list item...
    $('.thumbnailWrapper ul li').hover(function(){
        $(this).find('img').stop().animate({
            /* increase the image width for the zoom effect*/
            width: parseInt(thumbnail.imgWidth) + thumbnail.imgIncrease,
            /* we need to change the left and top position in order to
            have the zoom effect, so we are moving them to a negative
            position of the half of the imgIncrease */
            left: thumbnail.imgIncrease/2*(-1),
            top: thumbnail.imgIncrease/2*(-1)
        },{
            "duration": thumbnail.effectDuration,
            "queue": false
        });
        //show the caption using slideDown event
        $(this).find('.caption:not(:animated)').slideDown(
            thumbnail.effectDuration);
    //when mouse leave...
    }, function(){
        //find the image and animate it...
        $(this).find('img').animate({
            /* get it back to original size (zoom out) */
            width: thumbnail.imgWidth,
            /* get left and top positions back to normal */
            left: 0,
            top: 0
        }, thumbnail.effectDuration);
        //hide the caption using slideUp event
        $(this).find('.caption').slideUp(thumbnail.effectDuration);
    });
});
</script>
""" % {
    'increase': self.settings.thumbnailzoom_increase,
    'effectduration': self.settings.thumbnailzoom_effectduration,
}

    def css(self):
        style = '%s/thumbnailzoom/%s' % (
            self.staticFiles, self.settings.thumbnailzoom_style)

        if self.settings.thumbnailzoom_style == 'custom_style':
            style = '%s/%s' % (
                self.portal_url, self.settings.thumbnailzoom_custom_style)

        return u"""
<link rel="stylesheet" type="text/css" href="%s"/>
""" % style
ThumbnailzoomSettings = createSettingsFactory(ThumbnailzoomDisplayType.schema)
