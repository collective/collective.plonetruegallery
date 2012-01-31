from collective.plonetruegallery.interfaces import IFlickrAdapter, \
    IFlickrGallerySettings, IGalleryAdapter
from zope.interface import implements
from base import BaseAdapter
from collective.plonetruegallery import PTGMessageFactory as _

API_KEY = "9b354d88fb47b772fee4f27ab15d6854"

try:
    import flickrapi
except:
    pass


def add_condition():
    try:
        import flickrapi
    except:
        return False
    return True


class FlickrAdapter(BaseAdapter):
    implements(IFlickrAdapter, IGalleryAdapter)

    schema = IFlickrGallerySettings
    name = u"flickr"
    description = _(u"label_flickr_gallery_type",
        default=u"Flickr")

    sizes = {
        'small': {
            'width': 500,
            'height': 375
        },
        'medium': {
            'width': 640,
            'height': 480
        },
        'large': {
            'width': 1024,
            'height': 768
        },
        'thumb': {
            'width': 72,
            'height': 72
        },
        'flickr': {
            'small': '_m',
            'medium': '',
            'large': '_b'
        }
    }

    def assemble_image_information(self, image):
        return {
            'image_url': self.get_large_photo_url(image),
            'thumb_url': self.get_mini_photo_url(image),
            'link': self.get_photo_link(image),
            'title': image.get('title'),
            'description': ""
        }

    def get_flickr_user_id(self, username=None):
        if username is None:
            username = self.settings.flickr_username
        username = username.strip()

        try:
            return self.flickr.people_findByUsername(
                username=username).find('user').get('nsid')
        except:
            try:
                return self.flickr.people_getInfo(
                    user_id=username).find('person').get('nsid')
            except Exception, inst:
                self.log_error(Exception, inst, "Can't find filckr user id")

        return None

    def get_flickr_photoset_id(self, theset=None, userid=None):
        if userid is None:
            userid = self.get_flickr_user_id()
        userid = userid.strip()

        if theset is None:
            theset = self.settings.flickr_set
        theset = theset.strip()

        sets = self.flickr.photosets_getList(user_id=userid)

        for photoset in sets.find('photosets').getchildren():
            if photoset.find('title').text == theset or \
                    photoset.get('id') == theset:
                return photoset.get('id')

        return None

    def get_mini_photo_url(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (
            photo.get('farm'),
            photo.get('server'),
            photo.get('id'),
            photo.get('secret'),
        )

    def get_photo_link(self, photo):
        return "http://www.flickr.com/photos/%s/%s/sizes/o/" % (
            self.settings.flickr_username,
            photo.get('id')
        )

    def get_large_photo_url(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s%s.jpg" % (
            photo.get('farm'),
            photo.get('server'),
            photo.get('id'),
            photo.get('secret'),
            self.sizes['flickr'][self.settings.size]
        )

    @property
    def flickr(self):
        return  flickrapi.FlickrAPI(API_KEY)

    def retrieve_images(self):
        try:
            photos = self.flickr.photosets_getPhotos(
                user_id=self.get_flickr_user_id(),
                photoset_id=self.get_flickr_photoset_id(),
                media='photos'
            )

            return [self.assemble_image_information(image)
                for image in photos.find('photoset').getchildren()]
        except Exception, inst:
            self.log_error(Exception, inst, "Error getting all images")
            return []
