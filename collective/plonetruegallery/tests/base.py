# - coding: utf8 -
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

ztc.installProduct('collective.plonetruegallery')
ztc.installProduct('plone.app.blob')
ztc.installProduct('plone.app.imaging')
ztc.installProduct('plone.app.z3cform')
ptc.setupPloneSite(products=('collective.plonetruegallery',
                             'plone.app.blob',
                             'plone.app.imaging',
                             'plone.app.z3cform'))


class PTGTestCase(ptc.PloneTestCase):
    """
"""

    def get_gallery(self):
        return self.portal['test_gallery']

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory(id="test_gallery", type_name="Folder")
        populate_gallery(self.portal.test_gallery)


def populate_gallery(context):
    for i in range(1, 21):
        id = str(i)
        context.invokeFactory(id=id, type_name="Image")
        context[id].setDescription(u"Description for %i" % i +
            u'...and some unicode çòàéèÈ')
        context[id].setTitle("Title for %i" % i +
            u'...and some unicode çòàéèÈ')
        context[id].indexObject()
