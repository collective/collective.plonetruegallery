from z3c.form import validator, error
import zope.interface
import zope.component
import zope.schema
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery import PTGMessageFactory as _
from collective.plonetruegallery.browser.views.settings import \
    GallerySettingsForm


# monkey patch error reporting of default error view and
# make it work the obvious way it should be--without screwing up
# other implementions...
def createMessage(self):
    if len(self.error.args) == 2 and self.error.args[1] == True:
        return self.error.args[0]
    else:
        return self.error.doc()

error.ErrorViewSnippet.createMessage = createMessage


def empty(v):
    return v is None or len(v.strip()) == 0


class Data(object):

    def __init__(self, view):
        if isinstance(view, GallerySettingsForm):
            self.view = view
        elif isinstance(view.__parent__, GallerySettingsForm):
            self.view = view.__parent__
        else:
            raise ValueError(u"You need to provide the correct view to adapt.")

        self.widgets = {}
        for group in self.view.groups:
            self.widgets.update(group.widgets._data)

    def __getattr__(self, name):
        if name not in self.widgets.keys():
            raise KeyError(u"Can not find the name %s" % name)

        value = self.widgets[name].extract()
        if type(value) == list and len(value) == 1:
            return value[0]
        else:
            return value


