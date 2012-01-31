DEFAULT_GALLERY_TYPE = "default"
DEFAULT_DISPLAY_TYPE = 'classic'

from collective.plonetruegallery import PTGMessageFactory as _
from collective.plonetruegallery.meta.zcml import GalleryTypes, DisplayTypes

TRANSITIONS = (
    ('fade', _(u"label_fade", default=u'Fade')),
    ('show', _(u"label_show", default=u'Show'))
)
