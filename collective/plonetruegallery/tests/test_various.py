from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility
from zope.interface import alsoProvides

from collective.plonetruegallery.interfaces import IGallerySettings
from collective.plonetruegallery.settings import GallerySettings
from collective.ptg.galleria import IGalleriaDisplaySettings
from collective.plonetruegallery.tests import BaseTest
from collective.plonetruegallery.utils import getGalleryAdapter, \
    getDisplayAdapter
from collective.plonetruegallery.vocabularies import SizeVocabulary
from collective.plonetruegallery.vocabularies import GallerySearchabelTextSourceBinder
from plone import api
import unittest2 as unittest


class TestSettings(BaseTest):

    def test_settings_should_return_default_value(self):
        settings = GallerySettings(self.get_gallery())
        self.assertEqual(settings.gallery_type,
                         IGallerySettings['gallery_type'].default)

    def test_added_interface_settings_should_return_default_value(self):
        settings = GallerySettings(self.get_gallery(),
                                   interfaces=[IGalleriaDisplaySettings])
        self.assertEqual(settings.galleria_theme, 'light')

    def test_should_always_have_IGallerySettings_no_matter_what(self):
        settings = GallerySettings(self.get_gallery(), interfaces=[])
        self.assertTrue(IGallerySettings in settings._interfaces)

    def test_should_handle_passing_in_single_item(self):
        settings = GallerySettings(self.get_gallery(),
                                   interfaces=IGalleriaDisplaySettings)
        self.assertEqual(settings.galleria_theme, 'light')

    def test_should_return_default_to_None_if_it_is_not_in_an_interface(self):
        settings = GallerySettings(self.get_gallery())
        self.assertEqual(None, settings.foobar)


class TestUtils(BaseTest):

    def test_getGalleryAdapter(self):
        adapter = getGalleryAdapter(self.portal['test_gallery'], self.request)
        self.assertEqual(adapter.name, "basic")
        self.assertEqual(adapter.settings.gallery_type, "basic")

    def test_getDisplayAdapter(self):
        gadapter = getGalleryAdapter(self.portal['test_gallery'],
                                     self.request)
        displayer = getDisplayAdapter(gadapter)
        self.assertEqual(displayer.name, 'galleria')
        self.assertEqual(gadapter.settings.display_type, 'galleria')

    def test_getGalleryAdapter_when_asking_for_non_existant_type(self):
        gadapter = getGalleryAdapter(
            self.portal['test_gallery'], self.request, gallery_type="foobar")
        displayer = getDisplayAdapter(gadapter)
        self.assertEqual(displayer.name, 'galleria')
        self.assertEqual(gadapter.settings.display_type, 'galleria')
        self.assertEqual(gadapter.name, 'basic')
        self.assertEqual(gadapter.settings.gallery_type, 'basic')


class TestPloneAppImagingIntegration(BaseTest):

    def test_size_map_for_default_sizes_with_size_upgrades(self):
        props = getUtility(IPropertiesTool)
        imaging_properties = props.get('imaging_properties', None)
        if imaging_properties:
            adapter = getGalleryAdapter(self.portal['test_gallery'],
                                        self.request)
            self.assertEqual(adapter.sizes['small']['width'], 320)
            self.assertEqual(adapter.sizes['small']['height'], 320)
            self.assertEqual(adapter.sizes['medium']['width'], 576)
            self.assertEqual(adapter.sizes['medium']['height'], 576)
            self.assertEqual(adapter.sizes['large']['width'], 768)
            self.assertEqual(adapter.sizes['large']['height'], 768)

    def test_size_vocabulary_with_extra_allowed_sizes(self):
        props = getUtility(IPropertiesTool)
        imaging_properties = props.get('imaging_properties', None)
        if imaging_properties:
            imaging_properties.manage_changeProperties(
                allowed_sizes=['small 23:23', 'medium 42:42', 'big 91:91'])
        self.assertEqual(
            SizeVocabulary(None).by_token.keys(),
            ['small', 'large', 'medium', 'big'])


class TestGallerySearchableTextSourceBinder(BaseTest):

    def test_find_gallery_from_portlet(self):
        gallery = self.get_gallery()
        gallery.setLayout('galleryview')
        context = self.get_gallery().aq_parent
        gstsb = GallerySearchabelTextSourceBinder()
        gsts = gstsb(context)
        gen = gsts.search('')
        results = [res for res in gen]
        self.assertEqual(len(results), 1)

    def test_find_gallery_from_portlet_with_nav_root_custom(self):
        gallery = self.get_gallery()
        gallery.setLayout('galleryview')
        portal = api.portal.get()
        nav_root = api.content.create(
            container=portal,
            type='Folder',
            id='en')
        api.content.move(source=gallery, target=nav_root)
        from plone.app.layout.navigation.interfaces import INavigationRoot
        alsoProvides(nav_root, INavigationRoot)
        gstsb = GallerySearchabelTextSourceBinder()
        gsts = gstsb(nav_root)
        gen = gsts.search('')
        results = [res for res in gen]
        self.assertEqual(len(results), 1)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
