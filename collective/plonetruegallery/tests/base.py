import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from zope.configuration import xmlconfig

from cStringIO import StringIO

import sys

ztc.installProduct('collective.plonetruegallery')
ztc.installProduct('plone.app.blob')
ztc.installProduct('plone.app.imaging')
ztc.installProduct('plone.app.z3cform')
ptc.setupPloneSite(products=('collective.plonetruegallery', 'plone.app.blob', 'plone.app.imaging', 'plone.app.z3cform'))

class PTGTestCase(ptc.PloneTestCase):
    """
    """
    
    def get_gallery(self):
        return self.portal['test_gallery']
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        
        self.portal.invokeFactory(id="test_gallery", type_name="Folder")
        
        for i in range(1, 21):    
            self.portal['test_gallery'].invokeFactory(id=str(i), type_name="Image")
            self.portal['test_gallery'][str(i)].setDescription("Description for %i" % i)
            self.portal['test_gallery'][str(i)].setTitle("Title for %i" % i)
            self.portal['test_gallery'][str(i)].indexObject()
    
    
    
