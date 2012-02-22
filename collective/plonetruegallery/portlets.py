from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
import urllib

from plone.memoize.instance import memoize
from collective.plonetruegallery import PTGMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.plonetruegallery.vocabularies import \
    GallerySearchabelTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from utils import getGalleryAdapter


class IGalleryPortlet(IPortletDataProvider):

    show_title = schema.Bool(
        title=_(u"gallery_portlet_show_title_title", default=u"Show Title?"),
        description=_(u"gallery_portlet_show_title_description",
            default=u"Check to show the title of the gallery in the portlet"),
        default=True)

    gallery = schema.Choice(
        title=_(u"gallery_portlet_gallery_title", default=u"Gallery"),
        description=_(u"gallery_portlet_gallery_description",
            default=u"The gallery to show in this portlet."),
        source=GallerySearchabelTextSourceBinder(),
        required=True)

    mini = schema.Bool(
        title=_(u'gallery_portlet_mini', default=u"Mini gallery"),
        description=_(u'gallery_portlet_mini_desc',
                default=u"If false, the actual full gallery will render "
                        u"in an iframe and will follow the width and "
                        u"height settings"),
        default=True)

    width = schema.Int(
        title=_(u"gallery_portlet_width_title", default=u"Width"),
        description=_(u"gallery_portlet_width_description",
            default=u"The width of the image in the portlet"),
        required=True,
        default=200)

    height = schema.Int(
        title=_(u"gallery_portlet_height_title", default=u"Height"),
        description=_(u"gallery_portlet_height_description",
            default=u"The height of the image in the portlet."
                    u"If 0, no height is set."),
        required=True,
        default=0)

    timed = schema.Bool(
        title=_(u"gallery_portlet_timed_title", default=u"Timed"),
        description=_(u"gallery_portlet_timed_description",
            default=u"Do you want the gallery to be timed?"),
        required=True,
        default=True)

    hide_controls = schema.Bool(
        title=_(u"gallery_portlet_hide_controls", default="Hide Controls"),
        description=_(u"gallery_portlet_hide_controls_description",
            default="Hide portlet gallery controls"),
        required=False,
        default=False)


class GalleryAssignment(base.Assignment):
    implements(IGalleryPortlet)

    def __init__(self, show_title=True, gallery=None, width=200, timed=True,
                 hide_controls=False, mini=True, height=0):
        self.show_title = show_title
        self.gallery = gallery
        self.width = width
        self.timed = timed
        self._hide_controls = hide_controls
        self._mini = mini
        self._height = height

    def get_hide_controls(self):
        return getattr(self, '_hide_controls', False)

    def set_hide_controls(self, val):
        self._hide_controls = val
    hide_controls = property(get_hide_controls, set_hide_controls)

    def get_mini(self):
        return getattr(self, '_mini', True)

    def set_mini(self, val):
        self._mini = val
    mini = property(get_mini, set_mini)

    def get_height(self):
        return getattr(self, '_height', 0)

    def set_height(self, val):
        self._height = val
    height = property(get_height, set_height)

    @property
    def title(self):
        return "Plone True Gallery Portlet"


class PortletGalleryAdapter(object):

    def __init__(self, adapter):
        self.adapter = adapter
        self.request = adapter.request
        self.gallery_uid = self.adapter.gallery.UID()
        self.request_uid = self.request.get('portlet-gallery-uid',
                                            self.gallery_uid)
        self.request_index = int(self.request.get('portlet-gallery-index', 0))

    def image_link(self, image=None):
        if image is None:
            image = self.image

        return "%s/view?%s" % (
            self.adapter.gallery.absolute_url(),
            urllib.urlencode({'start_image': image['title']})
        )

    def next_image_url_params(self):
        index = self.request_uid == self.gallery_uid and \
                self.image_index + 1 or 1

        return urllib.urlencode({
            'portlet-gallery-uid': self.gallery_uid,
            'portlet-gallery-index': index
        })

    def prev_image_url_params(self):
        index = self.request_uid == self.gallery_uid and \
                self.image_index - 1 or -1

        return urllib.urlencode({
            'portlet-gallery-uid': self.gallery_uid,
            'portlet-gallery-index': index
        })

    @property
    def image_index(self):
        index = self.request_index
        num_images = self.adapter.number_of_images

        if index >= num_images:
            return 0
        elif index < 0:
            return num_images - 1

        return index

    @property
    def image(self):
        return self.adapter.cooked_images[self.image_index]


class GalleryRenderer(base.Renderer):

    render = ViewPageTemplateFile('gallery-portlet.pt')

    @property
    @memoize
    def gallery(self):
        try:
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            portal = portal_state.portal()
            path = self.data.gallery
            if path.startswith('/'):
                path = path[1:]

            return portal.restrictedTraverse(path, default=False)
        except:
            return False

    @property
    def style_classes(self):
        classes = 'portlet portletGallery'
        if self.data.timed:
            classes += ' timed'

        return classes

    def hide_controls(self):
        return getattr(self.data, 'hide_controls', False)

    @property
    @memoize
    def portlet_adapter(self):
        return PortletGalleryAdapter(self.gallery_adapter)

    @property
    def current_image(self):
        return self.portlet_adapter.image

    @property
    @memoize
    def gallery_adapter(self):
        return getGalleryAdapter(
            self.gallery,
            self.request
        )


class GalleryAddForm(base.AddForm):
    form_fields = form.Fields(IGalleryPortlet)
    form_fields['gallery'].custom_widget = UberSelectionWidget

    label = _(u"gallery_portlet_add_form_title", default=u"Add Gallery")
    description = _(u"gallery_portlet_add_form_description",
        default=u"This portlet allows you to show gallery"
                u"images in a portlet.")

    def create(self, data):
        return GalleryAssignment(**data)


class GalleryEditForm(base.EditForm):
    form_fields = form.Fields(IGalleryPortlet)
    form_fields['gallery'].custom_widget = UberSelectionWidget

    label = _(u"gallery_portlet_edit_form_description",
        default=u"Edit Gallery Portlet")
    description = _(u"gallery_portlet_add_form_description",
        default=u"This portlet allows you to show gallery images in a "
                u"portlet.")
