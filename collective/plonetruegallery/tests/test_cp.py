from collective.plonetruegallery.tests import BaseTest

from Products.CMFCore.utils import getToolByName

import unittest2 as unittest


class TestControlPanel(BaseTest):

    def test_control_panel_installed(self):
        cp = getToolByName(self.portal, 'portal_controlpanel')
        assert 'plonetruegallery' in [e['id'] for e in cp.listActionInfos()]


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
