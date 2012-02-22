from Products.CMFCore.interfaces import IPropertiesTool
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import alsoProvides
from zope.component import getUtility

from collective.plonetruegallery.settings import GallerySettings
from zope.publisher.browser import TestRequest
from collective.plonetruegallery.interfaces import IFlickrGallerySettings, \
    ISlideShowDisplaySettings, IGallerySettings
from base import PTGTestCase
from collective.plonetruegallery.utils import getGalleryAdapter, \
    getDisplayAdapter


class TestSettings(PTGTestCase):

    def test_settings_should_return_default_value(self):
        settings = GallerySettings(self.get_gallery())
        self.failUnless(settings.gallery_type == \
                        IGallerySettings['gallery_type'].default)

    def test_added_interface_settings_should_return_default_value(self):
        settings = GallerySettings(
            self.get_gallery(),
            interfaces=[ISlideShowDisplaySettings]
        )
        self.failUnless(settings.show_slideshow_infopane == \
            ISlideShowDisplaySettings['show_slideshow_infopane'].default)

    def test_should_always_have_IGallerySettings_no_matter_what(self):
        settings = GallerySettings(self.get_gallery(), interfaces=[])
        self.failUnless(IGallerySettings in settings._interfaces)

    def test_should_handle_passing_in_single_item(self):
        settings = GallerySettings(
            self.get_gallery(),
            interfaces=ISlideShowDisplaySettings
        )
        self.failUnless(IGallerySettings in settings._interfaces)
        self.failUnless(ISlideShowDisplaySettings in settings._interfaces)

    def test_should_return_default_to_None_if_it_is_not_in_an_interface(self):
        settings = GallerySettings(self.get_gallery())
        self.failUnless(None == settings.foobar)

    def test_should_set_setting_correctly(self):
        settings = GallerySettings(self.get_gallery())
        settings.gallery_type = "flickr"
        self.failUnless(settings.gallery_type == "flickr")

    def test_should_set_extra_interface_setting(self):
        settings = GallerySettings(
            self.get_gallery(),
            interfaces=[IFlickrGallerySettings]
        )
        settings.flickr_username = "john"
        self.failUnless(settings.flickr_username == "john")


class TestUtils(PTGTestCase):
    """
    """

    def test_getGalleryAdapter(self):
        adapter = getGalleryAdapter(self.portal['test_gallery'], TestRequest())
        self.failUnless(adapter.name == "basic")
        self.failUnless(adapter.settings.gallery_type == "basic")

    def test_getDisplayAdapter(self):
        gadapter = getGalleryAdapter(self.portal['test_gallery'],
                                     TestRequest())
        alsoProvides(IAttributeAnnotatable, gadapter.request)
        displayer = getDisplayAdapter(gadapter)
        self.failUnless(displayer.name == 'slideshow')
        self.failUnless(gadapter.settings.display_type == 'slideshow')

    def test_getGalleryAdapter_when_asking_for_non_existant_type(self):
        gadapter = getGalleryAdapter(
            self.portal['test_gallery'],
            TestRequest(),
            gallery_type="foobar"
        )
        alsoProvides(IAttributeAnnotatable, gadapter.request)
        displayer = getDisplayAdapter(gadapter)
        self.failUnless(displayer.name == 'slideshow')
        self.failUnless(gadapter.settings.display_type == 'slideshow')
        self.failUnless(gadapter.name == 'basic')
        self.failUnless(gadapter.settings.gallery_type == 'basic')


class TestPloneAppImagingIntegration(PTGTestCase):

    def test_size_map_for_default_sizes_with_size_upgrades(self):
        props = getUtility(IPropertiesTool)
        imaging_properties = props.get('imaging_properties', None)
        if imaging_properties:
            request = TestRequest()
            alsoProvides(request, IAttributeAnnotatable)
            adapter = getGalleryAdapter(self.portal['test_gallery'], request)
            self.assertEquals(adapter.sizes['small']['width'], 320)
            self.assertEquals(adapter.sizes['small']['height'], 200)
            self.assertEquals(adapter.sizes['medium']['width'], 576)
            self.assertEquals(adapter.sizes['medium']['height'], 400)
            self.assertEquals(adapter.sizes['large']['width'], 768)
            self.assertEquals(adapter.sizes['large']['height'], 768)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSettings))
    suite.addTest(makeSuite(TestUtils))
    suite.addTest(makeSuite(TestPloneAppImagingIntegration))
    return suite
