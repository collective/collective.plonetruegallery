from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility

from collective.plonetruegallery.settings import GallerySettings
from collective.plonetruegallery.interfaces import IFlickrGallerySettings, \
    IGallerySettings
from collective.ptg.galleria import IGalleriaDisplaySettings
from collective.plonetruegallery.tests import BaseTest
from collective.plonetruegallery.utils import getGalleryAdapter, \
    getDisplayAdapter

import unittest2 as unittest


class TestSettings(BaseTest):

    def test_settings_should_return_default_value(self):
        settings = GallerySettings(self.get_gallery())
        self.assertEquals(settings.gallery_type,
                        IGallerySettings['gallery_type'].default)

    def test_added_interface_settings_should_return_default_value(self):
        settings = GallerySettings(self.get_gallery(),
                                   interfaces=[IGalleriaDisplaySettings])
        self.assertEquals(settings.galleria_theme, 'light')

    def test_should_always_have_IGallerySettings_no_matter_what(self):
        settings = GallerySettings(self.get_gallery(), interfaces=[])
        self.failUnless(IGallerySettings in settings._interfaces)

    def test_should_handle_passing_in_single_item(self):
        settings = GallerySettings(self.get_gallery(),
                                   interfaces=IGalleriaDisplaySettings)
        self.assertEquals(settings.galleria_theme, 'light')

    def test_should_return_default_to_None_if_it_is_not_in_an_interface(self):
        settings = GallerySettings(self.get_gallery())
        self.assertEquals(None, settings.foobar)

    def test_should_set_setting_correctly(self):
        settings = GallerySettings(self.get_gallery())
        settings.gallery_type = "flickr"
        self.assertEquals(settings.gallery_type, "flickr")

    def test_should_set_extra_interface_setting(self):
        settings = GallerySettings(
            self.get_gallery(),
            interfaces=[IFlickrGallerySettings]
        )
        settings.flickr_username = "john"
        self.assertEquals(settings.flickr_username, "john")


class TestUtils(BaseTest):

    def test_getGalleryAdapter(self):
        adapter = getGalleryAdapter(self.portal['test_gallery'], self.request)
        self.assertEquals(adapter.name, "basic")
        self.assertEquals(adapter.settings.gallery_type, "basic")

    def test_getDisplayAdapter(self):
        gadapter = getGalleryAdapter(self.portal['test_gallery'],
                                     self.request)
        displayer = getDisplayAdapter(gadapter)
        self.assertEquals(displayer.name, 'galleria')
        self.assertEquals(gadapter.settings.display_type, 'galleria')

    def test_getGalleryAdapter_when_asking_for_non_existant_type(self):
        gadapter = getGalleryAdapter(self.portal['test_gallery'],
            self.request, gallery_type="foobar")
        displayer = getDisplayAdapter(gadapter)
        self.assertEquals(displayer.name, 'galleria')
        self.assertEquals(gadapter.settings.display_type, 'galleria')
        self.assertEquals(gadapter.name, 'basic')
        self.assertEquals(gadapter.settings.gallery_type, 'basic')


class TestPloneAppImagingIntegration(BaseTest):

    def test_size_map_for_default_sizes_with_size_upgrades(self):
        props = getUtility(IPropertiesTool)
        imaging_properties = props.get('imaging_properties', None)
        if imaging_properties:
            adapter = getGalleryAdapter(self.portal['test_gallery'],
                                        self.request)
            self.assertEquals(adapter.sizes['small']['width'], 320)
            self.assertEquals(adapter.sizes['small']['height'], 320)
            self.assertEquals(adapter.sizes['medium']['width'], 576)
            self.assertEquals(adapter.sizes['medium']['height'], 576)
            self.assertEquals(adapter.sizes['large']['width'], 768)
            self.assertEquals(adapter.sizes['large']['height'], 768)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
