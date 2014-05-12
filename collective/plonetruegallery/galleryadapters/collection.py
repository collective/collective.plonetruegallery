from zope.component import adapts
from Products.CMFCore.utils import getToolByName
from collective.plonetruegallery.galleryadapters.basic import \
    BasicTopicImageInformationRetriever as BTIIR
from Products.ATContentTypes.interface.image import IImageContent
from plone.app.collection.interfaces import ICollection
from collective.plonetruegallery.interfaces import IBasicAdapter
from plone.app.querystring import queryparser

try:
    from plone.app.contenttypes.behaviors.leadimage import ILeadImage
except ImportError:
    ILeadImage = None


class BasicCollectionImageInformationRetriever(BTIIR):
    adapts(ICollection, IBasicAdapter)

    def getImageInformation(self):
        limit = self.context.limit
        query = queryparser.parseFormquery(
            self.context, self.context.getRawQuery())
        if ILeadImage:
            query.update({
                'object_provides': {
                    'query': [
                        IImageContent.__identifier__,
                        ILeadImage.__identifier__],
                    'operator': 'or'
                }
            })
        else:
            query.update({'object_provides': IImageContent.__identifier__})
        query['sort_limit'] = limit
        catalog = getToolByName(self.context, 'portal_catalog')
        images = catalog(query)
        images = images[:limit]
        return map(self.assemble_image_information, images)
