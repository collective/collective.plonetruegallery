from z3c.form import validator, error
import zope.interface
import zope.component
import zope.schema
from collective.plonetruegallery.interfaces import IFlickrGallerySettings
from collective.plonetruegallery.interfaces import IPicasaGallerySettings
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


class FlickrSetValidator(validator.SimpleFieldValidator):

    def validate(self, photoset):
        super(FlickrSetValidator, self).validate(photoset)
        settings = Data(self.view)

        if settings.gallery_type != 'flickr':
            return

        if empty(photoset):
            raise zope.schema.ValidationError(
                _(u"label_validate_flickr_specify_user",
                    default=u"You must specify a flickr set to use."),
                True
            )

        try:
            adapter = getGalleryAdapter(self.context, self.request,
                                        settings.gallery_type)
            userid = adapter.get_flickr_user_id(settings.flickr_username)
            flickr_photosetid = adapter.get_flickr_photoset_id(photoset,
                                                               userid)

            if empty(flickr_photosetid):
                raise zope.schema.ValidationError(
                    _(u"label_validate_flickr_find_set",
                    default="Could not find flickr set."),
                    True
                )
        except:
            raise zope.schema.ValidationError(
                _(u"label_validate_flickr_find_set",
                default="Could not find flickr set."),
                True
            )
validator.WidgetValidatorDiscriminators(FlickrSetValidator,
    field=IFlickrGallerySettings['flickr_set'])
zope.component.provideAdapter(FlickrSetValidator)


class FlickrUsernameValidator(validator.SimpleFieldValidator):

    def validate(self, username):
        super(FlickrUsernameValidator, self).validate(username)

        settings = Data(self.view)
        if settings.gallery_type != 'flickr':
            return

        if empty(username):
            raise zope.schema.ValidationError(
                _(u"label_validate_flickr_specify_username",
                default=u"You must specify a username."),
                True
            )

        try:
            adapter = getGalleryAdapter(self.context, self.request,
                                        settings.gallery_type)
            flickr_userid = adapter.get_flickr_user_id(username)
            if empty(flickr_userid):
                raise zope.schema.ValidationError(
                    _(u"label_validate_flickr_user",
                    default=u"Could not find flickr user."),
                    True
                )
        except:
            raise zope.schema.ValidationError(_(u"label_validate_flickr_user",
                default=u"Could not find flickr user."),
                True
            )
validator.WidgetValidatorDiscriminators(FlickrUsernameValidator,
    field=IFlickrGallerySettings['flickr_username'])
zope.component.provideAdapter(FlickrUsernameValidator)


class PicasaUsernameValidator(validator.SimpleFieldValidator):

    def validate(self, username):
        settings = Data(self.view)
        if settings.gallery_type != 'picasa':
            return

        if empty(username):
            raise zope.schema.ValidationError(
                _(u"label_validate_picasa_specify_username",
                default=u"You must specify a picasa username."),
                True
            )
validator.WidgetValidatorDiscriminators(PicasaUsernameValidator,
    field=IPicasaGallerySettings['picasa_username'])
zope.component.provideAdapter(PicasaUsernameValidator)


class PicasaAlbumValidator(validator.SimpleFieldValidator):

    def validate(self, album):
        settings = Data(self.view)

        if settings.gallery_type != 'picasa':
            return

        username = settings.picasa_username

        if empty(album):
            raise zope.schema.ValidationError(
                _(u"label_validate_picasa_ablum_empty",
                default=u"You must specify a picasa album."),
                True
            )
        if empty(username):
            # do not continue validation until they have a valid username
            return
        adapter = getGalleryAdapter(self.context, self.request,
                                    gallery_type=settings.gallery_type)
        found = adapter.get_album_name(name=album, user=username)

        if found is None:
            raise zope.schema.ValidationError(
                _(u"label_validate_picasa_find_album",
                default=u"Could not find album."),
                True
            )
validator.WidgetValidatorDiscriminators(PicasaAlbumValidator,
    field=IPicasaGallerySettings['picasa_album'])
zope.component.provideAdapter(PicasaAlbumValidator)
