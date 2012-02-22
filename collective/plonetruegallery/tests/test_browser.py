import unittest

from Testing import ZopeTestCase as ztc

from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

from Products.Five.testbrowser import Browser
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from base import populate_gallery

from collective.plonetruegallery.settings import GallerySettings
import collective.plonetruegallery


@onsetup
def setUp():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.plonetruegallery)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.plonetruegallery')

setUp()
ptc.setupPloneSite(products=['collective.plonetruegallery'])


class TestViews(ptc.FunctionalTestCase):
    def test_gallery_views(self):
        browser = Browser()
        browser.handleErrors = False
        self.setRoles(('Manager',))
        self.portal.invokeFactory(id="test_gallery", type_name="Folder")
        gallery = self.portal.test_gallery
        self.portal.portal_workflow.doActionFor(gallery, 'publish')
        populate_gallery(gallery)
        gallery.setLayout('galleryview')
        settings = GallerySettings(gallery)
        vocab = getUtility(IVocabularyFactory,
            'collective.plonetruegallery.DisplayTypes')(gallery)
        title = gallery.objectValues()[0].Title()
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
            test_class=ptc.FunctionalTestCase),
        unittest.makeSuite(TestViews),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
