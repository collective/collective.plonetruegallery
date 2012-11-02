# coding: utf-8
from collective.plonetruegallery.testing import \
    PloneTrueGallery_INTEGRATION_TESTING, \
    PloneTrueGallery_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
import unittest2 as unittest
from plone.app.testing import TEST_USER_ID
from collective.plonetruegallery.testing import createObject
from os.path import join
from os.path import dirname

_images = join(dirname(__file__), 'test_images')


def populate_gallery(context):
    for i in range(1, 21):
        id = str(i)
        context.invokeFactory(id=id, type_name="Image")
        context[id].setDescription(u"Description for %i" % i +
            u'...and some unicode çòàéèÈ')
        context[id].setTitle("Title for %i" % i)
        context[id].indexObject()


class BaseTest(unittest.TestCase):

    layer = PloneTrueGallery_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.app = self.layer['app']
        #alsoProvides(self.request, ILayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(id="test_gallery", type_name="Folder")
        populate_gallery(self.portal.test_gallery)
        self.gallery = self.portal['test_gallery']

    def tearDown(self):
        pass

    def createImage(self, name="test.pdf", id='test1'):
        fi = createObject(self.portal, 'Image', id,
            file=open(join(_images, name)))
        return fi

    def get_gallery(self):
        return self.portal['test_gallery']


class BaseFunctionalTest(BaseTest):

    layer = PloneTrueGallery_FUNCTIONAL_TESTING
