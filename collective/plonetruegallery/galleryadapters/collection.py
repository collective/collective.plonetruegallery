from collective.plonetruegallery.galleryadapters.basic import (
    BasicTopicImageInformationRetriever as BTIIR,
)
from collective.plonetruegallery.interfaces import IBasicAdapter
from collective.plonetruegallery.interfaces import IGallery
from collective.plonetruegallery.interfaces import IGalleryAdapter
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IImage
from plone.app.querystring import queryparser
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from Products.ATContentTypes.interface.image import IImageContent
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor

import types


try:
    from plone.uuid.interfaces import IUUID
except:

    def IUUID(_, _2=None):
        return None


try:
    from plone.app.contenttypes.behaviors.leadimage import ILeadImage
except ImportError:
    ILeadImage = None


class BasicCollectionImageInformationRetriever(BTIIR):
    adapts(ICollection, IBasicAdapter)

    def __init__(self, context, gallery_adapter):
        self.pm = getToolByName(context, 'portal_membership')
        self.context = context
        self.gallery_adapter = gallery_adapter

        def get_subgalleries(self, **kwargs):
            def fix_query(parsedquery):
                index_modifiers = getUtilitiesFor(IParsedQueryIndexModifier)
                for name, modifier in index_modifiers:
                    if name in parsedquery:
                        new_name, query = modifier(parsedquery[name])
                        parsedquery[name] = query
                        # if a new index name has been returned, we need to
                        # replace the native ones
                        if name != new_name:
                            del parsedquery[name]
                            parsedquery[new_name] = query
                return parsedquery

            query = queryparser.parseFormquery(
                self.gallery, self.gallery.query
            )
            catalog = getToolByName(self.gallery, 'portal_catalog')
            if 'Subject' in kwargs:
                if 'Subject' not in query:
                    query.update({'Subject': kwargs['Subject']})
                else:
                    query['Subject'] = {
                        'operator': 'and',
                        'query': [kwargs['Subject']]
                        + query['Subject']['query'],
                    }

            if 'object_provides' not in query:
                query.update({'object_provides': IGallery.__identifier__})
            else:
                query['object_provides'] = {
                    'operator': 'and',
                    'query': [IGallery.__identifier__]
                    + query['object_provides']['query'],
                }

            query = fix_query(query)

            sort_order = (
                'reverse' if self.gallery.sort_reversed else 'ascending'
            )
            b_size = self.gallery.item_count
            sort_on = self.gallery.sort_on
            limit = self.gallery.limit

            results = catalog(
                query,
                b_size=b_size,
                sort_on=sort_on,
                sort_order=sort_order,
                limit=limit,
            )

            uid = IUUID(self.gallery, None)
            if uid is None:
                uid = self.gallery.UID()

            def afilter(i):
                """prevent same object and multiple nested galleries"""
                return (
                    i.UID != uid
                    and getMultiAdapter(
                        (i.getObject(), self.request),
                        name='plonetruegallery_util',
                    ).enabled()
                )

            return filter(afilter, results)

        self.gallery_adapter.get_subgalleries = types.MethodType(
            get_subgalleries, self.gallery_adapter
        )

    def getImageInformation(self):
        limit = self.context.limit
        query = queryparser.parseFormquery(self.context, self.context.query)

        if ILeadImage:
            query.update(
                {
                    'object_provides': {
                        'query': [
                            IImage.__identifier__,
                            ILeadImage.__identifier__,
                        ],
                        'operator': 'or',
                    }
                }
            )
        else:
            query.update({'object_provides': IImage.__identifier__})
        query['sort_limit'] = limit
        query = self.fix_query(query)
        catalog = getToolByName(self.context, 'portal_catalog')
        images = catalog(query)
        images = images[:limit]
        return map(self.assemble_image_information, images)

    def fix_query(self, parsedquery):
        index_modifiers = getUtilitiesFor(IParsedQueryIndexModifier)
        for name, modifier in index_modifiers:
            if name in parsedquery:
                new_name, query = modifier(parsedquery[name])
                parsedquery[name] = query
                # if a new index name has been returned, we need to replace
                # the native ones
                if name != new_name:
                    del parsedquery[name]
                    parsedquery[new_name] = query
        return parsedquery
