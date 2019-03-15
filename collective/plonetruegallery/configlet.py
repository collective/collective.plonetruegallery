# -*- coding: utf-8 -*-
from collective.plonetruegallery.browser.views.settings import (
    GallerySettingsForm,
)
from collective.plonetruegallery.i18n import PTGMessageFactory as _
from plone.app.z3cform.layout import wrap_form
from z3c.form import button

import zope.i18n


class PloneTruegalleryControlPanelForm(GallerySettingsForm):
    label = _(u"PloneTruegallery Default Settings")
    description = _(u'Default settings to use for all galleries on site.')

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        msg = changes and self.successMessage or self.noChangesMessage
        self.status = zope.i18n.translate(msg)


PloneTruegalleryControlPanelView = wrap_form(PloneTruegalleryControlPanelForm)
