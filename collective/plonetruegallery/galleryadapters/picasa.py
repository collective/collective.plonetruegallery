from collective.plonetruegallery.interfaces import IPicasaAdapter, \
    IPicasaGallerySettings, IGalleryAdapter
from zope.interface import implements
from base import BaseAdapter
from collective.plonetruegallery import PTGMessageFactory as _

try:
    import gdata.photos.service
    from gdata.photos.service import GooglePhotosException
except:
    pass


def add_condition():
    try:
        import gdata.photos.service
        from gdata.photos.service import GooglePhotosException
    except:
        return False
    return True

GDATA = {}
DATA_FEED_URL = '/data/feed/api/user/%s/album' + \
                '/%s?kind=photo&imgmax=%s&thumbsize=%sc'


class PicasaAdapter(BaseAdapter):
    implements(IPicasaAdapter, IGalleryAdapter)

    schema = IPicasaGallerySettings
    name = u"picasa"
    description = _(u"label_picasa_gallery_type",
        default=u"Picasa Web Albums")

    sizes = {
        'small': {
            'width': 320,
            'height': 320
        },
        'medium': {
            'width': 576,
            'height': 576
        },
        'large': {
            'width': 800,
            'height': 800
        },
        'thumb': {
            'width': 72,
            'height': 72
        }
    }

    def get_gd_client(self):
        uid = self.gallery.UID()
        if uid in GDATA:
            return GDATA[uid]
        else:
            self.gd_client = gdata.photos.service.PhotosService()
            return GDATA[uid]

    def set_gd_client(self, value):
        GDATA[self.gallery.UID()] = value

    gd_client = property(get_gd_client, set_gd_client)

    def assemble_image_information(self, image):
        return {
            'image_url': image.content.src,
            'thumb_url': image.media.thumbnail[0].url,
            'link': image.content.src,
            'title': image.title.text,
            'description': image.summary.text or ''
        }

    def get_album_name(self, name=None, user=None):
        if name is None:
            name = self.settings.picasa_album
        name = name.strip()

        if user is None:
            user = self.settings.picasa_username
        user = user.strip()

        feed = self.gd_client.GetUserFeed(user=user)
        for entry in feed.entry:
            if entry.name.text.decode("utf-8") == name or \
                entry.title.text.decode("utf-8") == name:
                return entry.name.text

        return None

    def feed(self):
        gd_client = self.gd_client

        try:
            url = DATA_FEED_URL % (
                self.settings.picasa_username,
                self.get_album_name(),
                self.sizes[self.settings.size]['width'],
                self.sizes['thumb']['width']
            )
            feed = gd_client.GetFeed(url)
            return feed
        except GooglePhotosException, inst:
            #Do not show anything if connection failed
            self.log_error(GooglePhotosException, inst,
                "Error getting photo feed")
            return None

    def retrieve_images(self):
        try:
            picasaGallery = self.feed()
            images = [self.assemble_image_information(i)
                for i in picasaGallery.entry]
            return images
        except Exception, inst:
            self.log_error(Exception, inst, "Error getting all images")
            return []
