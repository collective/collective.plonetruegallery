from .interfaces import IPloneTruegalleryConfiguration


from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.form import ControlPanelForm
from Products.CMFCore.interfaces import IPropertiesTool

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapts, getUtility
from zope.formlib.form import FormFields
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

_ = MessageFactory('collective.plonetruegallery')

class PloneTruegalleryControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IPloneTruegalleryConfiguration)
    
    def __init__(self, context):
        super(PloneTruegalleryControlPanelAdapter, self).__init__(context)
        self.context = getUtility(IPropertiesTool).plonetruegallery_properties

    default_gallery = ProxyFieldProperty(IPloneTruegalleryConfiguration['default_gallery'])

class PloneTruegalleryControlPanel(ControlPanelForm):
    form_fields = FormFields(IPloneTruegalleryConfiguration)
    label = _(u"PloneTruegallery configuration.")
    description = _(u'Settings to configure collective.plonetruegallery.')
    form_name = _(u'PloneTruegallery settings')
    def _on_save(self, data=None):
        pass