from zope.interface import implements
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from interfaces import IGallerySettings


class GallerySettings(object):
    """
    Just uses Annotation storage to save and retrieve the data...
    """
    implements(IGallerySettings)

    # these are settings for defaults that are not listed
    # in the interface because I don't want them to show up
    # in the schema
    defaults = {
        'last_cooked_time_in_seconds': 0,
        'cooked_images': []
    }

    def __init__(self, context, interfaces=[IGallerySettings]):
        """
        The interfaces argument allows you to customize which
        interface these settings implemenet.
        """
        self.context = context

        self._interfaces = interfaces
        if type(self._interfaces) not in (list, tuple):
            self._interfaces = [self._interfaces]
        self._interfaces = list(self._interfaces)
        if IGallerySettings not in self._interfaces:
            self._interfaces.append(IGallerySettings)

        annotations = IAnnotations(context)

        self._metadata = annotations.get('collective.plonetruegallery', None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations['collective.plonetruegallery'] = self._metadata

    def __setattr__(self, name, value):
        if name in ('context', '_metadata', '_interfaces', 'defaults'):
            self.__dict__[name] = value
        else:
            self._metadata[name] = value

    def __getattr__(self, name):
        """
        since we have multiple settings that are possible to be used
        here, we have to interate over those interfaces to find the
        default values here.
        """
        default = None

        if name in self.defaults:
            default = self.defaults[name]

        for iface in self._interfaces:
            if name in iface.names():
                default = iface[name].default

        return self._metadata.get(name, default)
