from collective.plonetruegallery.tests import BaseTest

from zope.component import getMultiAdapter
from collective.plonetruegallery.meta.zcml import getAllGalleryTypes
from collective.plonetruegallery.config import named_adapter_prefix
from collective.plonetruegallery.config import DISPLAY_NAME_VIEW_PREFIX
from collective.plonetruegallery.utils import getAllDisplayTypes
from Products.CMFCore.utils import getToolByName
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType

import unittest2 as unittest


class TestRegistration(BaseTest):

    def test_gallerytypes_registered(self):
        gallerytypes = getAllGalleryTypes()

        for t in gallerytypes:
            adapter = getMultiAdapter((self.gallery, self.request),
                                      name=named_adapter_prefix + t.name)
            self.failUnless(isinstance(adapter, t))

    def test_displaytypes_registered(self):
        displaytypes = getAllDisplayTypes()
        for t in displaytypes:
            adapter = getMultiAdapter((self.gallery, self.request),
                                      name=DISPLAY_NAME_VIEW_PREFIX + t.name)
            self.failUnless(isinstance(adapter, t))


class TestBasicAdapter(BaseTest):

    def get_basic_adapter(self):
        return getMultiAdapter((self.gallery, self.request),
                               name=named_adapter_prefix + 'basic')

    def test_should_cook_images_on_invoking(self):
        adapter = self.get_basic_adapter()

        self.assertEquals(len(adapter.cooked_images), 20)
        self.assertEquals(adapter.number_of_images, 20)

    def test_should_order_images_according_to_folder_order(self):
        adapter = self.get_basic_adapter()

        first_image = self.gallery[self.gallery.objectIds()[0]]
        self.assertEquals(first_image.Title(),
                          adapter.cooked_images[0]['title'])

        self.gallery.moveObjectsByDelta(first_image.getId(), 1)
        plone_utils = getToolByName(self.gallery, 'plone_utils')
        plone_utils.reindexOnReorder(self.gallery)

        adapter = self.get_basic_adapter()
        first_image = self.gallery[self.gallery.objectIds()[0]]
        self.assertEquals(first_image.Title(),
                          adapter.cooked_images[0]['title'])


class TestBatchingDisplayType(BaseTest):

    def get_basic_adapter(self):
        return getMultiAdapter((self.gallery, self.request),
                               name=named_adapter_prefix + 'basic')

    def test_should_handle_exceeding_batch_size(self):
        self.request.form.update({'start_image': 'Title for 14'})
        displayer = BatchingDisplayType(self.gallery, self.request)
        displayer.adapter.settings.batch_size = 5

        self.assertEquals(displayer.start_image_index, 3)
        self.assertEquals(displayer.b_start, 10)
        self.assertEquals(displayer.get_page(), 2)

    def test_should_work_no_start_no_batch(self):
        displayer = BatchingDisplayType(self.gallery, self.request)
        displayer.adapter.settings.batch_size = 5

        self.assertEquals(displayer.start_image_index, 0)
        self.assertEquals(displayer.b_start, 0)
        self.assertEquals(displayer.get_page(), 0)

    def test_with_b_start_specified(self):
        self.request.form.update({'b_start': '10'})
        displayer = BatchingDisplayType(self.gallery, self.request)
        displayer.adapter.settings.batch_size = 5

        self.assertEquals(displayer.start_image_index, 0)
        self.assertEquals(displayer.b_start, 10)
        self.assertEquals(displayer.get_page(), 0)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
