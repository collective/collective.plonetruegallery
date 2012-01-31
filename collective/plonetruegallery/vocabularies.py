from zope.component import getUtilitiesFor
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from collective.plonetruegallery.interfaces import IGallerySettings
from collective.plonetruegallery.interfaces import IDisplayType
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.vocabularies.catalog import SearchableTextSource
from plone.app.vocabularies.catalog import parse_query
from collective.plonetruegallery.interfaces import IGallery
from Products.CMFCore.utils import getToolByName


class PTGVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value...
    This prevents any issues if a gallery or display
    type is removed and the user had it selected.
    """

    def __init__(self, terms, *interfaces, **config):
        super(PTGVocabulary, self).__init__(terms, *interfaces)
        if 'default' in config:
            self.default = config['default']
        else:
            self.default = None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.default]
        except:
            raise LookupError(value)


def DisplayTypeVocabulary(context):
    terms = []
    utils = list(getUtilitiesFor(IDisplayType))
    for name, utility in sorted(utils, key=lambda x: x[1].name):
        if utility.name:
            name = utility.name or name
            terms.append(SimpleTerm(name, name, utility.description))

    return PTGVocabulary(terms,
                default=IGallerySettings['display_type'].default)


def GalleryTypeVocabulary(context):
    from collective.plonetruegallery.meta.zcml import GalleryTypes
    items = []
    for t in GalleryTypes:
        items.append(SimpleTerm(t.name, t.name, t.description))

    return PTGVocabulary(items,
                default=IGallerySettings['gallery_type'].default)


class GallerySearchableTextSource(SearchableTextSource):

    def search(self, query_string):
        results = super(GallerySearchableTextSource, self).search(query_string)
        utils = getToolByName(self.context, 'plone_utils')
        query = self.base_query.copy()
        if query_string == '':
            if self.default_query is not None:
                query.update(parse_query(self.default_query, self.portal_path))
        else:
            query.update(parse_query(query_string, self.portal_path))
        try:
            results = self.catalog(**query)
        except:
            results = []

        utils = getToolByName(self.context, 'plone_utils')
        for result in results:
            try:
                if utils.browserDefault(result.getObject())[1][0] ==\
                                                        "galleryview":
                    yield result.getPath()[len(self.portal_path):]
            except:
                pass


class GallerySearchabelTextSourceBinder(SearchableTextSourceBinder):

    def __init__(self):
        self.query = {'object_provides': IGallery.__identifier__}
        self.default_query = 'path:'

    def __call__(self, context):
        return GallerySearchableTextSource(
            context,
            base_query=self.query.copy(),
            default_query=self.default_query
        )
