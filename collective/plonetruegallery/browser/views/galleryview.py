from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.utils import getDisplayAdapter
from Products.CMFCore.utils import getToolByName
from collective.plonetruegallery.settings import GallerySettings
from collective.plonetruegallery.portlets import PortletGalleryAdapter
from collective.plonetruegallery.interfaces import IBatchingDisplayType


class GalleryView(BrowserView):

    subgallery_template = ViewPageTemplateFile('subgallery.pt')

    def __call__(self):
        self.adapter = getGalleryAdapter(self.context, self.request)
        self.displayer = getDisplayAdapter(self.adapter)
        self.settings = GallerySettings(
            self.context,
            interfaces=[self.adapter.schema, self.displayer.schema]
        )

        return self.index()

    def is_batch(self):
        return IBatchingDisplayType.providedBy(self.displayer)

    @memoize
    def show_subgalleries(self):
        return self.adapter.settings.show_subgalleries and \
            self.adapter.contains_sub_galleries

    def getAdaptedGallery(self, gallery):
        return getGalleryAdapter(gallery, self.request)


class ForceCookingOfImages(BrowserView):

    def __call__(self):
        adapter = getGalleryAdapter(self.context, self.request)
        adapter.cook()
        self.request.response.redirect(self.context.absolute_url())


class ForceCookingOfAllGalleries(BrowserView):

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        for gallery in catalog.searchResults(portal_type="Gallery"):
            gallery = gallery.getObject()

            self.request.response.write("cooking %s, located at %s\n" % (
                gallery.Title(), gallery.absolute_url()))

            adapter = getGalleryAdapter(gallery, self.request)
            adapter.cook()

        self.request.response.write("Timer is up!  Finished cooking!")


class AJAX(BrowserView):

    def get_image(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        uid = self.request.get('portlet-gallery-uid', None)
        if not uid:
            return "bad request..."

        obj = catalog(UID=uid)[0].getObject()
        adapter = getGalleryAdapter(obj, self.request)
        portlet_adapter = PortletGalleryAdapter(adapter)
        image = portlet_adapter.image

        return str({
            'src': image['image_url'],
            'title': image['title'],
            'description': image['description'],
            'image-link': portlet_adapter.image_link(),
            'next-url': portlet_adapter.next_image_url_params(),
            'prev-url': portlet_adapter.prev_image_url_params()
        })
