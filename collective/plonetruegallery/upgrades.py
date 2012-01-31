from settings import GallerySettings
from Products.CMFCore.utils import getToolByName
import transaction


def replace_gallery_objects(portal):
    """
    I'm not sure this is not the most optimal. I could do a just
    do a depth-first search of the object graph, but with large site,
    this could take a very long time. I still think in most cases,
    this is the best way to go. Also, you need to start at each base
    gallery folder as Folders are not allowed inside Galleries.
    """

    catalog = portal.portal_catalog
    
    galleries = catalog.searchResults(portal_type="Gallery")
    
    while len(galleries) > 0:
        old_gallery = galleries[0].getObject()
        
        parent = old_gallery.getParentNode()
        while parent.portal_type == "Gallery":
            old_gallery = parent
            parent = old_gallery.getParentNode()
        
        old_id = old_gallery.getId()
        new_gallery = parent[parent.invokeFactory("Folder",
            parent.generateUniqueId())]

        # select gallery view
        new_gallery.setLayout('galleryview')

        # copy contents over
        cb_copy_data = old_gallery.manage_copyObjects(old_gallery.objectIds())
        new_gallery.manage_pasteObjects(cb_copy_data)

        #copy fields over..
        #replace most fields....
        fields_not_to_replace = ('id', 'type', 'size', 'displayType',
                                 'showCarousel', 'showInfopane', 'isTimed',
                                 'delay', 'imageChangeDuration',
                                 'classicTransition', 'slideshowEffect')

        for field in old_gallery.schema.fields():
            if field.__name__ not in fields_not_to_replace:
                new_gallery.getField(field.__name__).set(
                    new_gallery, field.get(old_gallery))

        new_settings = GallerySettings(new_gallery)
        new_settings.gallery_type = old_gallery.getType() == "default" and \
            "basic" or old_gallery.getType()
        new_settings.size = old_gallery.getSize()
        new_settings.display_type = old_gallery.getDisplayType() == "classic" \
            and "slideshow" or old_gallery.getDisplayType()
        new_settings.show_slideshow_carousel = old_gallery.getShowCarousel()
        new_settings.show_slideshow_infopane = old_gallery.getShowInfopane()
        new_settings.timed = old_gallery.getIsTimed()
        new_settings.delay = old_gallery.getDelay()
        new_settings.duration = old_gallery.getImageChangeDuration()
        new_settings.slideshow_effect = old_gallery.getSlideshowEffect()
        new_settings.picasa_username = getattr(old_gallery, 'picasaUsername',
                                               None)
        new_settings.picasa_album = getattr(old_gallery, 'picasaAlbum', None)
        new_settings.flickr_username = getattr(old_gallery, 'flickrUsername',
                                               None)
        new_settings.flickr_set = getattr(old_gallery, 'flickrSet', None)

        # delete old gallery
        parent.manage_delObjects([old_id])
        transaction.commit()

        # rename new gallery to old id
        new_gallery.setId(old_id)
        new_gallery.reindexObject()

        galleries = catalog.searchResults(portal_type="Gallery")

default_profile = 'profile-collective.plonetruegallery:default'
to_08a1_profile = 'profile-collective.plonetruegallery:upgrade_to_0_8a1'


def upgrade_to_0_8a1(context):
    site = getToolByName(context, 'portal_url').getPortalObject()
    replace_gallery_objects(site)
    context.runAllImportStepsFromProfile(to_08a1_profile)
    context.runAllImportStepsFromProfile(default_profile)


def check_should_upgrade_to_0_8_1a3(context):
    try:
        return int(context.getLastVersionForProfile(
            default_profile.lstrip('profile-'))[0]) < 7
    except:
        return True


def upgrade_to_0_8_1a3(context):
    context.runImportStepFromProfile(default_profile, 'portlets')
    context.runImportStepFromProfile(default_profile, 'jsregistry')
    context.runImportStepFromProfile(default_profile, 'cssregistry')


def check_should_upgrade_to_0_9_0b1(context):
    return False


def upgrade_to_0_9_0b1(context):
    pass


def upgrade_to_1_0_5(context):
    jsregistry = getToolByName(context, 'portal_javascripts')
    jsregistry.unregisterResource('++resource++mootools.js')
    jsregistry.unregisterResource('++resource++slideshow.js')
