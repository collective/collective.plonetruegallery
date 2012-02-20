from collective.plonetruegallery import PTGMessageFactory as _
from zope.interface import Interface
from plone.z3cform.fieldsets import group as plonegroup
from z3c.form import form, field, group, button
from plone.app.z3cform.layout import wrap_form
from collective.plonetruegallery.interfaces import IGallerySettings
from collective.plonetruegallery.meta.zcml import getAllGalleryTypes
from collective.plonetruegallery.utils import getDisplayType
from collective.plonetruegallery.utils import getAllDisplayTypes
from collective.plonetruegallery.settings import GallerySettings
import zope.i18n


class INothing(Interface):
    pass


class MainSettingsGroup(plonegroup.Group):
    fields = field.Fields(IGallerySettings)
    label = _(u"Main")


class GallerySettingsForm(group.GroupForm, form.EditForm):
    """
    The page that holds all the gallery settings
    """

    fields = field.Fields(INothing)
    groups = [MainSettingsGroup]

    label = _(u'heading_gallery_settings_form', default=u'Gallery')
    description = _(u'description_gallery_settings_form',
        default=u'Configure the parameters for this gallery.')

    successMessage = _(u'successMessage_gallery_settings_form',
        default=u'Gallery Settings Saved.')
    noChangesMessage = _(u'noChangesMessage_gallery_settings_form',
        default=u'There are no changes in the Gallery settings.')

    def add_fields_to_group(self, type_, groupname):
        group = None
        for g in self.groups:
            if groupname == g.label:
                group = g

        if group is None:
            g = plonegroup.GroupFactory(groupname, field.Fields(type_.schema))
            self.groups.append(g)
        else:
            fields = field.Fields(type_.schema)
            toadd = []
            for f in fields._data_values:
                if f.__name__ not in group.fields.keys():
                    toadd.append(f)

            group.fields = field.Fields(group.fields, *toadd)

    def update(self):
        gallerytypes = getAllGalleryTypes()
        displaytypes = getAllDisplayTypes()
        for t in gallerytypes:
            if len(t.schema.names()) > 0:
                self.add_fields_to_group(t, t.name)

        for t in displaytypes:
            if len(t.schema.names()) > 0:
                self.add_fields_to_group(t, t.name)

        super(GallerySettingsForm, self).update()

    def set_status_message(self, settings, has_changes):
        display_type = getDisplayType(settings.display_type)
        msg = has_changes and self.successMessage or self.noChangesMessage
        msg = zope.i18n.translate(msg)

        if display_type.userWarning is not None:
            self.status = "%s %s" % (msg,
                zope.i18n.translate(display_type.userWarning))
        else:
            self.status = msg

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        settings = GallerySettings(self.context)

        has_changes = False
        if changes:
            settings = GallerySettings(self.context)
            settings.last_cooked_time_in_seconds = 0
            has_changes = True

        self.set_status_message(settings, has_changes)

GallerySettingsView = wrap_form(GallerySettingsForm)
