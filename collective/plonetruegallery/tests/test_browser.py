import unittest2 as unittest

from Testing import ZopeTestCase as ztc

from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

from plone.testing.z2 import Browser
from collective.plonetruegallery.tests import populate_gallery

from collective.plonetruegallery.settings import GallerySettings
from collective.plonetruegallery.tests import BaseFunctionalTest
from collective.plonetruegallery.testing import browserLogin


class TestViews(BaseFunctionalTest):
    def test_gallery_views(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        browserLogin(self.portal, browser)
        self.portal.invokeFactory(id="test_gallery", type_name="Folder")
        gallery = self.portal.test_gallery
        self.portal.portal_workflow.doActionFor(gallery, 'publish')
        populate_gallery(gallery)
        gallery.setLayout('galleryview')
        settings = GallerySettings(gallery)
        vocab = getUtility(IVocabularyFactory,
            'collective.plonetruegallery.DisplayTypes')(gallery)
        title = gallery.objectValues()[0].Title()
        import transaction
        transaction.commit()
        for display_type in vocab.by_value.keys():
            settings.display_type = display_type
            # This test doesn't trigger the same error as seen in real plone
            # caused by unicode characters in image titles
            browser.open(gallery.absolute_url())
            self.assertTrue(title in browser.contents)


def test_suite():
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            'browser.txt', package='collective.plonetruegallery',
            test_class=BaseFunctionalTest),
        unittest.makeSuite(TestViews),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
