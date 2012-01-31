from base import PTGTestCase

from zope.component import getMultiAdapter, getAdapter
from zope.publisher.browser import TestRequest
from collective.plonetruegallery.meta.zcml import getAllGalleryTypes
from collective.plonetruegallery.config import named_adapter_prefix
from collective.plonetruegallery.utils import getAllDisplayTypes
from Products.CMFCore.utils import getToolByName
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType


class TestRegistration(PTGTestCase):

    def test_gallerytypes_registered(self):
        gallerytypes = getAllGalleryTypes()

        for t in gallerytypes:
            adapter = getMultiAdapter(
                (self.portal['test_gallery'], TestRequest()),
                name=named_adapter_prefix + t.name
            )
            self.failUnless(isinstance(adapter, t))

    def test_displaytypes_registered(self):
        displaytypes = getAllDisplayTypes()

        gadapter = getMultiAdapter(
            (self.portal['test_gallery'], TestRequest()),
            name=named_adapter_prefix + "basic"
        )
        for t in displaytypes:
            adapter = getAdapter(gadapter, name=named_adapter_prefix + t.name)
            self.failUnless(isinstance(adapter, t))


class TestBasicAdapter(PTGTestCase):

    def get_basic_adapter(self):
        return getMultiAdapter(
            (self.portal['test_gallery'], TestRequest()),
            name=named_adapter_prefix + 'basic'
        )

    def test_should_cook_images_on_invoking(self):
        adapter = self.get_basic_adapter()

        self.failUnless(len(adapter.cooked_images) == 20)
        self.failUnless(adapter.number_of_images == 20)

    def test_should_order_images_according_to_folder_order(self):
        adapter = self.get_basic_adapter()
        gallery = self.portal['test_gallery']

        first_image = gallery[gallery.objectIds()[0]]
        self.failUnless(first_image.Title() == \
                            adapter.cooked_images[0]['title'])

        gallery.moveObjectsByDelta(first_image.getId(), 1)
        plone_utils = getToolByName(gallery, 'plone_utils')
        plone_utils.reindexOnReorder(gallery)

        adapter = self.get_basic_adapter()
        first_image = gallery[gallery.objectIds()[0]]
        self.failUnless(first_image.Title() == \
                        adapter.cooked_images[0]['title'])


class TestBatchingDisplayType(PTGTestCase):

    def get_basic_adapter(self):
        return getMultiAdapter(
            (self.portal['test_gallery'], TestRequest()),
            name=named_adapter_prefix + 'basic'
        )

    def test_should_automatically_bring_you_to_correct_batch_if_image_exceeds_batch_size(self):
        adapter = getMultiAdapter(
            (
                self.portal['test_gallery'],
                TestRequest(form={'start_image': 'Title for 14'})
            ),
            name=named_adapter_prefix + 'basic'
        )
        adapter.settings.batch_size = 5
        displayer = BatchingDisplayType(adapter)

        self.failUnless(displayer.start_image_index == 3)
        self.failUnless(displayer.b_start == 10)
        self.failUnless(displayer.get_page() == 2)

    def test_should_work_normally_if_no_start_image_is_selected_and_no_batch(self):
        adapter = getMultiAdapter(
            (self.portal['test_gallery'], TestRequest()),
            name=named_adapter_prefix + 'basic'
        )
        adapter.settings.batch_size = 5
        displayer = BatchingDisplayType(adapter)

        self.failUnless(displayer.start_image_index == 0)
        self.failUnless(displayer.b_start == 0)
        self.failUnless(displayer.get_page() == 0)

    def test_with_b_start_specified(self):
        adapter = getMultiAdapter(
            (
                self.portal['test_gallery'],
                TestRequest(form={'b_start': '10'})
            ),
            name=named_adapter_prefix + 'basic'
        )
        adapter.settings.batch_size = 5
        displayer = BatchingDisplayType(adapter)

        self.failUnless(displayer.start_image_index == 0)
        self.failUnless(displayer.b_start == 10)
        self.failUnless(displayer.get_page() == 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRegistration))
    suite.addTest(makeSuite(TestBasicAdapter))
    return suite
