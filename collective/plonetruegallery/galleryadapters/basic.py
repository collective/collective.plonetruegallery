from collective.plonetruegallery.interfaces import IBasicAdapter, \
    IBasicGallerySettings, IImageInformationRetriever, IGalleryAdapter
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import adapts
from base import BaseAdapter, BaseImageInformationRetriever
from collective.plonetruegallery import PTGMessageFactory as _
from Products.ATContentTypes.interface.image import IImageContent
from Products.ATContentTypes.interface import IATTopic
try:
    from plone.folder.interfaces import IFolder as IBaseFolder
except ImportError:
    from Products.Archetypes.interfaces import IBaseFolder
from plone.memoize.view import memoize_contextless
from plone.memoize.instance import memoize
has_pai = True
try:
    import plone.app.imaging.utils
except ImportError:
    has_pai = False
try:
    from plone.app.contenttypes.behaviors.leadimage import ILeadImage
except ImportError:
    ILeadImage = None
try:
    from plone.app.contenttypes.interfaces import IImage
except ImportError:
    IImage = None

IMAGE_IFACES = filter(None, [IImageContent, ILeadImage, IImage])


class BasicAdapter(BaseAdapter):
    implements(IBasicAdapter, IGalleryAdapter)

    name = u"basic"
    description = _(
        u"label_default_gallery_type", default=u"Use Plone To Manage Images")

    schema = IBasicGallerySettings
    cook_delay = 0

    # since some default sizes Plone has are rather small,
    # let's setup a mechanism to upgrade sizes.

    minimum_sizes = {
        'small': {
            'width': 320,
            'height': 320,
            'next_scale': 'preview'
        },
        'medium': {
            'width': 576,
            'height': 576,
            'next_scale': 'large'
        }
    }

    @property
    @memoize_contextless
    def size_map(self):
        image_sizes = {
            'small': 'mini',
            'medium': 'preview',
            'large': 'large',
            'thumb': 'tile'
        }

        # Here we try to get the custom sizes
        # we skip some scales, since they are already 'taken'
        try:
            from plone.app.imaging.utils import getAllowedSizes
            all_sizes = getAllowedSizes()
            for scale_name in all_sizes.keys():
                if scale_name not in ['small', 'medium', 'mini', 'preview',
                                      'thumb', 'tile', 'large']:
                    image_sizes[str(scale_name)] = str(scale_name)
        except (ImportError, AttributeError):
            # plone 3 without plone.app.blob... We still have defaults...
            pass
        return image_sizes

    @property
    @memoize_contextless
    def _inverted_size_map(self):
        return dict([(v, k) for (k, v) in self.size_map.iteritems()])

    @property
    @memoize_contextless
    def sizes(self):
        if has_pai:
            from plone.app.imaging.utils import getAllowedSizes
            # user has plone.app.imaging installed, use
            # these image size settings
            _allowed_sizes = getAllowedSizes()
            allowed_sizes = {}

            for scale_name, sizes in _allowed_sizes.items():
                width, height = sizes
                if scale_name not in self._inverted_size_map:
                    continue
                size_name = self._inverted_size_map[scale_name]
                allowed_sizes[size_name] = {'width': width, 'height': height}

                if size_name in self.minimum_sizes:
                    if width < self.minimum_sizes[size_name]['width']:
                        allowed_sizes[size_name]['width'] = \
                            self.minimum_sizes[size_name]['width']
                    if height < self.minimum_sizes[size_name]['height']:
                        allowed_sizes[size_name]['height'] = \
                            self.minimum_sizes[size_name]['height']

                    self.size_map[size_name] = \
                        self.minimum_sizes[size_name]['next_scale']

            return allowed_sizes
        else:
            from Products.ATContentTypes.content.image import ATImageSchema
            return {
                'small': {
                    'width': 320,
                    'height': 320
                },
                'medium': {
                    'width': 576,
                    'height': 576
                },
                'large': {
                    'width': ATImageSchema['image'].sizes['large'][0],
                    'height': ATImageSchema['image'].sizes['large'][1]
                },
                'thumb': {
                    'width': ATImageSchema['image'].sizes['tile'][0],
                    'height': ATImageSchema['image'].sizes['tile'][1]
                }
            }

    def retrieve_images(self):
        adapter = getMultiAdapter(
            (self.gallery, self),
            IImageInformationRetriever)
        return adapter.getImageInformation()

    def cook(self):
        """
        do not cook anything since we don't have a cook_delay on this
        type anyway
        """
        pass

    @property
    @memoize
    def cooked_images(self):
        return self.retrieve_images()


class BasicImageInformationRetriever(BaseImageInformationRetriever):
    implements(IImageInformationRetriever)
    adapts(IBaseFolder, IBasicAdapter)

    def getImageInformation(self):
        """
        A catalog search should be faster especially when there
        are a large number of images in the gallery. No need
        to wake up all the image objects.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        gallery_path = self.context.getPhysicalPath()
        images = catalog.searchResults(
            object_provides=[_.__identifier__ for _ in IMAGE_IFACES],
            path='/'.join(gallery_path),
            sort_on='getObjPositionInParent'
        )

        # filter out image images that are not directly in its path..
        filterfunc = lambda i:\
            len(i.getPath().split('/')) == len(gallery_path) + 1
        images = filter(filterfunc, images)
        return map(self.assemble_image_information, images)

    def get_link_url(self, image):
        retval = super(BasicImageInformationRetriever, self).\
            get_link_url(image)
        if self.pm.isAnonymousUser():
            return retval
        return retval + "/view"


class BasicTopicImageInformationRetriever(BaseImageInformationRetriever):
    implements(IImageInformationRetriever)
    adapts(IATTopic, IBasicAdapter)

    def getImageInformation(self):
        query = self.context.buildQuery()
        if query is not None:
            should_limit = self.context.getLimitNumber()
            limit = self.context.getItemCount()
            if not limit:  # also make sure we have more than 0 items
                should_limit = False
            if should_limit:
                query['sort_limit'] = limit
            try:
                query.update({'object_provides': {
                             'query': [_.__identifier__ for _ in IMAGE_IFACES],
                             'operator': 'or'}})
            except:
                query.update({
                    'object_provides': [
                        _.__identifier__ for _ in IMAGE_IFACES]})
            catalog = getToolByName(self.context, 'portal_catalog')
            images = catalog(query)
            if should_limit:
                images = images[:limit]
            return map(self.assemble_image_information, images)
        else:
            return []

    def get_link_url(self, image):
        retval = super(BasicTopicImageInformationRetriever, self).\
            get_link_url(image)
        if self.pm.isAnonymousUser():
            return retval
        return retval + "/view"
