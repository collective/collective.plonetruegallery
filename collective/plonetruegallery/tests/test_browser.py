import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import collective.plonetruegallery


@onsetup
def setUp():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.plonetruegallery)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.plonetruegallery')

setUp()
ptc.setupPloneSite(products=['collective.plonetruegallery'])


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='collective.plonetruegallery',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='collective.plonetruegallery.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.plonetruegallery',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='collective.plonetruegallery',
            test_class=ptc.FunctionalTestCase)
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
