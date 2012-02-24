from collective.plonetruegallery.interfaces import IDisplayType
from collective.plonetruegallery.interfaces import IFancyBoxDisplaySettings
from collective.plonetruegallery.interfaces import IHighSlideDisplaySettings
from collective.plonetruegallery.interfaces import IBatchingDisplayType
from collective.plonetruegallery.interfaces import IGallerifficDisplaySettings
from collective.plonetruegallery.interfaces import IGalleriaDisplaySettings
from collective.plonetruegallery.interfaces import IS3sliderDisplaySettings
from collective.plonetruegallery.interfaces import IPikachooseDisplaySettings
from collective.plonetruegallery.interfaces import INivosliderDisplaySettings
from collective.plonetruegallery.interfaces import INivogalleryDisplaySettings
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


class FancyBoxDisplayType(BatchingDisplayType):

    name = u"fancybox"
    schema = IFancyBoxDisplaySettings
    description = _(u"label_fancybox_display_type",
        default=u"Fancy Box")

    def javascript(self):
        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++collective.fancybox/jquery.easing-1.3.pack.js"></script>
<script type="text/javascript"
    src="%(portal_url)s/++resource++collective.fancybox/jquery.mousewheel-3.0.4.pack.js"></script>
<script type="text/javascript"
    src="%(portal_url)s/++resource++collective.fancybox/jquery.fancybox.js"></script>
  <script type="text/javascript">
    var auto_start = %(start_automatically)s;
    var start_image_index = %(start_index_index)i;
    (function($){
        $(document).ready(function() {
            $("a.fancyzoom-gallery").fancybox({
                'type': 'image',
                'transitionIn': 'elastic',
                'transitionOut': 'elastic'});
            var images = $('a.fancyzoom-gallery');
            if(images.length <= start_image_index){
                start_image_index = 0;
            }
            if(auto_start){
                $(images[start_image_index]).trigger('click');
            }
        });
    })(jQuery);
    </script>
        """ % {
            'start_automatically': str(self.start_automatically).lower(),
            'start_index_index': self.start_image_index,
            'portal_url': self.portal_url
        }

    def css(self):
        return u"""
<link rel="stylesheet" type="text/css"
    href="%(staticFiles)s/jquery.fancybox.css" media="screen" />
""" % {'staticFiles': self.staticFiles}
FancyBoxSettings = createSettingsFactory(FancyBoxDisplayType.schema)


class HighSlideDisplayType(BatchingDisplayType):

    name = u"highslide"
    schema = IHighSlideDisplaySettings
    description = _(u"label_highslide_display_type",
        default=u"Highslide - verify terms of use")
    userWarning = _(u"label_highslide_user_warning",
        default=u"You can only use the Highslide gallery for non-commercial "
                u"use unless you purchase a commercial license. "
                u"Please visit http://highslide.com/ for details."
    )

    def css(self):
        return u"""
<link rel="stylesheet" type="text/css"
    href="%(portal_url)s/++resource++collective.js.highslide/highslide.css" />
""" % {'portal_url': self.portal_url}

    def javascript(self):
        outlineType = "hs.outlineType = '%s';" % \
                            self.settings.highslide_outlineType
        wrapperClassName = ''

        if 'drop-shadow' in outlineType:
            wrapperClassName = 'dark borderless floating-caption'
            outlineType = ''
        elif 'glossy-dark' in outlineType:
            wrapperClassName = 'dark'
        if len(wrapperClassName) == 0:
            wrapperClassName = 'null'
        else:
            wrapperClassName = "'%s'" % wrapperClassName

        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++collective.js.highslide/highslide-with-gallery.js"></script>

<!--[if lt IE 7]>
<link rel="stylesheet" type="text/css"
  href="%(portal_url)s/++resource++collective.js.highslide/highslide-ie6.css" />
<![endif]-->

<script type="text/javascript">
hs.graphicsDir = '%(portal_url)s/++resource++collective.js.highslide/graphics/';
hs.align = 'center';
hs.transitions = ['expand', 'crossfade'];
hs.fadeInOut = true;
hs.dimmingOpacity = 0.8;
%(outlineType)s
hs.wrapperClassName = %(wrapperClassName)s;
hs.captionEval = 'this.thumb.alt';
hs.marginBottom = 105; // make room for the thumbstrip and the controls
hs.numberPosition = 'caption';
hs.autoplay = %(timed)s;
hs.transitionDuration = %(duration)i;
hs.addSlideshow({
    interval: %(delay)i,
    repeat: true,
    useControls: true,
    fixedControls: 'fit',
    overlayOptions: {
        position: 'middle center',
        opacity: .7,
        hideOnMouseOut: true
    },
    thumbstrip: {
        position: 'bottom center',
        mode: 'horizontal',
        relativeTo: 'viewport'
    }
});

var auto_start = %(start_automatically)s;
var start_image_index = %(start_index_index)i;

(function($){
$(document).ready(function() {
    var images = $('a.highslide');
    if(images.length <= start_image_index){
        start_image_index = 0;
    }
    if(auto_start){
        $(images[start_image_index]).trigger('click');
    }
});
})(jQuery);
</script>
        """ % {
            'outlineType': outlineType,
            'wrapperClassName': wrapperClassName,
            'delay': self.settings.delay,
            'timed': jsbool(self.settings.timed),
            'duration': self.settings.duration,
            'start_automatically': jsbool(
                self.start_automatically or self.settings.timed),
            'start_index_index': self.start_image_index,
            'portal_url': self.portal_url
        }
HighSlideSettings = createSettingsFactory(HighSlideDisplayType.schema)


class GallerifficDisplayType(BaseDisplayType):

    name = u"galleriffic"
    schema = IGallerifficDisplaySettings
    description = _(u"label_galleriffic_display_type",
        default=u"Galleriffic")

    def css(self):
        return u"""
<link rel="stylesheet" type="text/css"
    href="%(staticFiles)s/galleriffic/css/style.css" />

<style>
div.slideshow-container,div.loader,div.slideshow a.advance-link{
    height: %(height)ipx;
    width: %(box_width)ipx;
}
span.image-caption {
    width: %(width)ipx;
}
div.slideshow a.advance-link{
    line-height: %(height)ipx;
}
div.slideshow span.image-wrapper a img{
    max-width: %(width)ipx;
    max-height: %(height)ipx;
}

ul.thumbs li{
    height: %(thumbnail_height)ipx;
}
</style>
""" % {
            'staticFiles': self.staticFiles,
            'height': self.height,
            'width': self.width,
            'box_width': self.width + 10,
            'thumbnail_height': self.adapter.sizes['thumb']['height']
        }

    def javascript(self):
        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++jquery.galleriffic.js"></script>
<script type="text/javascript"
    src="%(portal_url)s/++resource++jquery.opacityrollover.js"></script>
<script type="text/javascript">
    document.write('<style>.noscript { display: none; }</style>');

(function($){
$(document).ready(function() {

    // Initially set opacity on thumbs and add
    // additional styling for hover effect on thumbs
    var onMouseOutOpacity = 0.67;
    var captionOpacity = 0.7;
    $('#thumbs ul.thumbs li').opacityrollover({
        mouseOutOpacity:   onMouseOutOpacity,
        mouseOverOpacity:  1.0,
        fadeSpeed:         'fast',
        exemptionSelector: '.selected'
    });
    // Initialize Advanced Galleriffic Gallery
    var gallery = $('#thumbs').galleriffic({
        delay:                     %(delay)i,
        numThumbs:                 %(batch_size)i,
        preloadAhead:              10,
        enableTopPager:            true,
        enableBottomPager:         true,
        maxPagesToShow:            7,
        imageContainerSel:         '#slideshow',
        controlsContainerSel:      '#controls',
        captionContainerSel:       '#caption',
        loadingContainerSel:       '#loading',
        renderSSControls:          true,
        renderNavControls:         true,
        playLinkText:              'Play Slideshow',
        pauseLinkText:             'Pause Slideshow',
        prevLinkText:              '&lsaquo; Previous Photo',
        nextLinkText:              'Next Photo &rsaquo;',
        nextPageLinkText:          'Next &rsaquo;',
        prevPageLinkText:          '&lsaquo; Prev',
        enableHistory:             true,
        autoStart:                 %(timed)s,
        syncTransitions:           true,
        defaultTransitionDuration: %(duration)i,
        onSlideChange:             function(prevIndex, nextIndex) {
            this.find('ul.thumbs').children()
                .eq(prevIndex).fadeTo('fast', onMouseOutOpacity).end()
                .eq(nextIndex).fadeTo('fast', 1.0);
        },
        onTransitionOut:           function(slide, caption, isSync, callback) {
            slide.fadeTo(this.getDefaultTransitionDuration(isSync), 0.0, callback);
            caption.fadeTo(this.getDefaultTransitionDuration(isSync), 0.0);
        },
        onTransitionIn:            function(slide, caption, isSync) {
            var duration = this.getDefaultTransitionDuration(isSync);
            slide.fadeTo(duration, 1.0);
            var slideImage = slide.find('img');
            caption.width(slideImage.width())
                .css({
                    'bottom' : Math.floor((slide.height() - slideImage.outerHeight()) / 2),
                    'left' : Math.floor((slide.width() - slideImage.width()) / 2) + slideImage.outerWidth() - slideImage.width()
                })
                .fadeTo(duration, captionOpacity);
        },
        onPageTransitionOut:       function(callback) {
            this.fadeTo('fast', 0.0, callback);
        },
        onPageTransitionIn:        function() {
            this.fadeTo('fast', 1.0);
        },
        onImageAdded:              function(imageData, $li) {
            $li.opacityrollover({
                mouseOutOpacity:   onMouseOutOpacity,
                mouseOverOpacity:  1.0,
                fadeSpeed:         'fast',
                exemptionSelector: '.selected'
            });
        }
    });
});
})(jQuery);

</script>
""" % {
    'portal_url': self.portal_url,
    'timed': jsbool(self.settings.timed),
    'delay': self.settings.delay,
    'duration': self.settings.duration,
    'batch_size': self.settings.batch_size
}
GallerifficSettings = createSettingsFactory(GallerifficDisplayType.schema)


class GalleriaDisplayType(BaseDisplayType):

    name = u"galleria"
    schema = IGalleriaDisplaySettings
    description = _(u"label_galleria_display_type",
        default=u"Galleria")

    js_theme_files = {
        'dark': '++resource++plonetruegallery.resources/galleria/dark.js',
        'light': '++resource++plonetruegallery.resources/galleria/light.js',
        'classic': '++resource++collective.galleria.classic.js'
    }
    css_theme_files = {
        'dark': '++resource++plonetruegallery.resources/galleria/dark.css',
        'light': '++resource++plonetruegallery.resources/galleria/light.css',
        'classic': '++resource++collective.galleria.classic.css'
    }

    def css(self):
        return u"""
<link rel="stylesheet" type="text/css"
    href="%(portal_url)s/%(css_file)s" />
<style>
#galleria{
    height: %(height)ipx;
}
</style>
""" % {
            'portal_url': self.portal_url,
            'height': self.height + 60,
            'css_file': self.css_theme_files[self.settings.galleria_theme]
        }

    def javascript(self):
        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++collective.galleria.js"></script>
<script type="text/javascript"
    src="%(portal_url)s/%(js_file)s"></script>
<script type="text/javascript">
(function($){
$(document).ready(function() {
    // Initialize Galleria
    $('#galleria').galleria({
        theme: 'classic',
        transitionSpeed: %(duration)i,
        transition: "%(transition)s",
        autoplay: %(autoplay)s,
        clicknext: true,
        showInfo: %(showInfo)s
    });
});
})(jQuery);

</script>
""" % {
    'portal_url': self.portal_url,
    'js_file': self.js_theme_files[self.settings.galleria_theme],
    'duration': self.settings.duration,
    'transition': self.settings.galleria_transition,
    'autoplay': self.settings.timed and str(self.settings.delay) or 'false',
    'showInfo': jsbool(self.settings.galleria_auto_show_info)
}
GalleriaSettings = createSettingsFactory(GalleriaDisplayType.schema)


class S3sliderDisplayType(BaseDisplayType):

    name = u"s3slider"
    schema = IS3sliderDisplaySettings
    description = _(u"label_s3slider_display_type",
        default=u"s3slider")

    def javascript(self):
        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++s3Slider.js"></script>

<script type="text/javascript">
$(document).ready(function() {
   $('#s3slider').s3Slider({
      timeOut: %(delay)i
   });
})(jQuery);
</script>
        """ % {
        'portal_url': self.portal_url,
        'delay': self.settings.delay
        }

    def css(self):
        return u"""
        <style>
#s3slider {
   height: %(height)ipx;
   width: %(width)ipx;
   position: relative;
   overflow: hidden;
}

ul#s3sliderContent {
   width: %(width)ipx;
   position: absolute;
   top: 0;
   margin-left: 0;
   overflow: hidden !important;
}

.s3sliderImage {
   float: left;
   position: relative;
   display: none;
}

.s3sliderImage span {
   position: absolute;
   left: 0;
   font: 10px/15px Arial, Helvetica, sans-serif;
   padding: 20px 13px;
   background-color: #000;
   filter: alpha(opacity=70);
   -moz-opacity: 0.7;
   -khtml-opacity: 0.7;
   opacity: 0.7;
   color: #fff;
   display: none;
   top: 0;
   height: %(height)ipx;
   width: %(textwidth)ipx;
}

ul#s3sliderContent li {
    text-decoration: none;
    list-style-image: none;
    list-style-type: none;
}

div.image-title {
    font-size: 16px;
    margin-bottom: 4px;
}

.clear {
   clear: both;
}
 </style>

""" % {
        'staticFiles': self.staticFiles,
        'height': self.height,
        'width': self.width,
        'textwidth': self.width / 5
       }

S3sliderSettings = createSettingsFactory(S3sliderDisplayType.schema)


class PikachooseDisplayType(BaseDisplayType):

    name = u"pikachoose"
    schema = IPikachooseDisplaySettings
    description = _(u"label_pikachoose_display_type",
        default=u"Pikachoose")

    def javascript(self):
        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++jquery.pikachoose.js"></script>
<script type="text/javascript"
    src="%(portal_url)s/++resource++jquery.jcarousel.js"></script>
<script language="javascript">
$(document).ready(function(){
    var preventStageHoverEffect = function(self){
        self.wrap.unbind('mouseenter').unbind('mouseleave');
        self.imgNav.append('<a class="tray"></a>');
        self.imgNav.show();
        self.hiddenTray = true;
        self.imgNav.find('.tray').bind('click',function(){
            if(self.hiddenTray){
                self.list.parents('.jcarousel-container.jcarousel-container-vertical').animate({height:"%(verticalheight)ipx"});
                self.list.parents('.jcarousel-container.jcarousel-container-horizontal').animate({height:"80px"});
            }else{
                self.list.parents('.jcarousel-container').animate({height:"1px"});
            }
            self.hiddenTray = !self.hiddenTray;
        });
    }
    $("#pikame").PikaChoose({
        bindsFinished: preventStageHoverEffect,
        transition:[%(transition)i],
        animationSpeed: %(duration)i,
        fadeThumbsIn: %(fadethumbsin)s,
        speed: %(speed)s,
        carouselVertical: %(vertical)s,
        showCaption: %(showcaption)s,
        thumbOpacity: 0.4,
        autoPlay: %(autoplay)s,
        carousel: 'false',
        showTooltips: %(showtooltips)s });
});
</script>
""" % {
        'portal_url': self.portal_url,
        'duration': self.settings.duration,
        'speed': self.settings.delay,
        'transition': self.settings.pikachoose_transition,
        'autoplay': jsbool(self.settings.timed),
        'text': '{ play: "", stop: "", previous: "Previous", next: "Next", loading: "Loading" }',
        'showcaption': jsbool(self.settings.pikachoose_showcaption),
        'showtooltips': jsbool(self.settings.pikachoose_showtooltips),
        'carousel': jsbool(self.settings.pikachoose_showcarousel),
        'vertical': jsbool(self.settings.pikachoose_vertical),
        'thumbopacity': 0.4,
        'fadethumbsin': 'false',
        'verticalheight': self.height - 18,
    }

    def css(self):
        return u"""
        <style>
.pikachoose,
.pika-stage {
   height: %(height)ipx;
   width: %(width)ipx;
}

.pika-stage {
   height: %(height)ipx;
   width: %(width)ipx;
}

.pika-stage, .pika-thumbs li{
    background-color: #%(backgroundcolor)s;
}

.jcarousel-skin-pika .jcarousel-container-vertical,
.jcarousel-skin-pika .jcarousel-clip-vertical {
   height: %(lowerheight)ipx;
</style>
<link rel="stylesheet" type="text/css" href="++resource++plonetruegallery.resources/pikachoose/css/style.css"/>
""" % {
        'height': self.height,
        'width': self.width,
        'lowerheight': self.height - 18,
        'backgroundcolor': self.settings.pikachoose_backgroundcolor,
    }
PikachooseSettings = createSettingsFactory(PikachooseDisplayType.schema)


class NivosliderDisplayType(BatchingDisplayType):

    name = u"nivoslider"
    schema = INivosliderDisplaySettings
    description = _(u"label_nivoslider_display_type",
        default=u"Nivoslider")

    def javascript(self):
        return u"""
<script type="text/javascript" src="%(portal_url)s/++resource++jquery.nivo.slider.pack.js"></script>
<script type="text/javascript">
$(window).load(function() {
    $('#slider').nivoSlider({
        effect: '%(effect)s', // Specify sets like: 'fold,fade,sliceDown'
        slices: %(slices)i, // For slice animations
        boxCols: %(boxcols)i, // For box animations
        boxRows: %(boxrows)i, // For box animations
        animSpeed: %(animspeed)i, // Slide transition speed
        pauseTime: %(delay)i, // How long each slide will show
        directionNav: %(directionnav)s, // Next & Prev navigation
        directionNavHide: %(directionnavhide)s, // Only show on hover
        controlNav: true, // 1,2,3... navigation
        controlNavThumbs: true, // Use thumbnails for Control Nav
        controlNavThumbsFromRel: true, // Use image rel for thumbs
        pauseOnHover: %(pauseonhover)s, // Stop animation while hovering
        randomStart: %(randomstart)s // Start on a random slide
    });
});
</script>
""" % {
         'portal_url': self.portal_url,
         'height': self.height,
         'effect': self.settings.nivoslider_effect,
         'slices': self.settings.nivoslider_slices,
         'boxcols': self.settings.nivoslider_boxcols,
         'boxrows': self.settings.nivoslider_boxrows,
         'animspeed': self.settings.duration,
         'delay': self.settings.delay,
         'directionnav': jsbool(self.settings.nivoslider_directionnav),
         'directionnavhide': jsbool(self.settings.nivoslider_directionnavhide),
         'pauseonhover': jsbool(self.settings.nivoslider_pauseonhover),
         'randomstart': jsbool(self.settings.nivoslider_randomstart)
    }

    def css(self):
        return u"""
        <style>
        .nivoSlider {
        height: %(height)s !important;
        width: %(width)s !important;
        }
        a.nivo-imageLink {
        height: 200px;
        }
        </style>
<link rel="stylesheet" type="text/css" href="++resource++plonetruegallery.resources/nivoslider/css/nivoslider.css"/>
<link rel="stylesheet" type="text/css" href="++resource++plonetruegallery.resources/nivoslider/css/%(nivoslider_theme)s/style.css"/>
""" % {
        'height': self.settings.nivoslider_height,
        'width': self.settings.nivoslider_width,
        'nivoslider_theme': self.settings.nivoslider_theme,
       }
NivosliderSettings = createSettingsFactory(NivosliderDisplayType.schema)


class NivogalleryDisplayType(BaseDisplayType):

    name = u"nivogallery"
    schema = INivogalleryDisplaySettings
    description = _(u"label_nivogallery_display_type",
        default=u"Nivogallery")

    def javascript(self):
        return u"""
        <script type="text/javascript"
    src="%(portal_url)s/++resource++jquery.nivo.gallery.min.js"></script>
    <script type="text/javascript">
$(document).ready(function() {
    $('#gallery').nivoGallery({
    pauseTime: %(delay)i,
    animSpeed: %(duration)i,
    effect: 'fade',
    startPaused: false,
    directionNav: %(directionnav)s,
    progressBar: %(progressbar)s
    });
});
</script>

""" % {
         'portal_url': self.portal_url,
         'duration': self.settings.duration,
         'timed': jsbool(self.settings.timed),
         'delay': self.settings.delay,
         'start_automatically': jsbool(self.settings.timed),
         'directionnav': jsbool(self.settings.nivogallery_directionnav),
         'progressbar': jsbool(self.settings.nivogallery_progressbar),
    }

    def css(self):
        return u"""
        <style>
       .nivoGallery {
        height: %(height)s;
        width: %(width)s;
        }
        </style>
<link rel="stylesheet" type="text/css" href="++resource++plonetruegallery.resources/nivogallery/css/style.css"/>
""" % {
        'height': self.settings.nivogallery_height,
        'width': self.settings.nivogallery_width,
       }

NivogallerySettings = createSettingsFactory(NivogalleryDisplayType.schema)
