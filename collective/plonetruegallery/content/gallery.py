from collective.plonetruegallery.interfaces import IGallery
from collective.plonetruegallery.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.base import registerATCT
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from config import *
from collective.plonetruegallery import PTGMessageFactory as _
from collective.plonetruegallery.meta.zcml import GalleryTypes

copied_fields = {}
copied_fields['title'] = ATFolderSchema['title'].copy()
copied_fields['title'].widget.label = _(u"label_gallery_name", default=u"Gallery Name")

schema = Schema(
    (
    copied_fields['title'],

    StringField(
        name="type",
        widget=SelectionWidget(
            label=_(u"label_gallery_type", default=u"Type"),
            description=_(u"description_gallery_type", 
                default=u"Select the type of gallery you want this to be.  "
                        u"If you select something other than default, you "
                        u"must fill out the information in the corresponding tab for that gallery type.")
        ),
        vocabulary="get_gallery_types_vocabulary",
        default=DEFAULT_GALLERY_TYPE,
        enforceVocabulary = True,
        required=True
    ),
    StringField(
        name="size",
        widget=SelectionWidget(
            label=_(u"label_gallery_size", default=u"Size")
        ),
        vocabulary=(
            ('small', _(u"label_size_small", default=u'Small')),
            ('medium', _(u"label_size_medium", default=u'Medium')),
            ('large', _(u"label_size_large", default=u'Large'))
        ),
        default="medium",
        enforceVocabulary = True
    ),
    StringField(
        name="displayType",
        widget=SelectionWidget(
            label=_(u"label_gallery_display_type", default=u"Gallery Display Type"),
            description=_(
                u"label_gallery_display_type_description",
                default=u"Choose the method in which the gallery should be displayed"
            )
        ),
        vocabulary="get_display_types_vocabulary",
        default=DEFAULT_DISPLAY_TYPE,
        enforceVocabulary = True,
    ),
    BooleanField(
        name="showCarousel",
        widget=BooleanField._properties['widget'](
            label=_(u"label_show_carousel", default=u"Show Carousel?"),
        ),
        default=True,
        schemata="advanced"
    ),
    BooleanField(
        name="showInfopane",
        widget=BooleanField._properties['widget'](
            label=_(u"label_show_info_pane", default=u"Show Info pane?"),
        ),
        default=True,
        schemata="advanced"
    ),
    BooleanField(
        name="isTimed",
        widget=BooleanField._properties['widget'](
            label=_(u"label_timed", default=u"Timed?"),
            description=_(u"description_timed", 
                default=u"Should this gallery automatically change images for the user?"),
        ),
        default=True,
        schemata="advanced"
    ),
    IntegerField(
        name='delay',
        widget=IntegerField._properties['widget'](
            label=_(u"label_delay", default=u"Delay"),
            description=_(u"description_delay", 
                default=u"If slide show is timed, the delay sets how long before the next image is shown in miliseconds.")
        ),
        required=1,
        default=5000,
        schemata="advanced"
    ),
    IntegerField(
        name='imageChangeDuration',
        widget=IntegerField._properties['widget'](
            label=_(u"label_image_change_duration", default=u"Change Duration"),
            description=_(u"description_fade_in_duration", 
                default=u"The amount of time the change effect should take in miliseconds."
            )
        ),
        required=1,
        default=500,
        schemata="advanced"
    ),
    StringField(
        name="classicTransition",
        widget=SelectionWidget(
            label=_(u"label_transition", default=u"Transition"),
            description=_(u"description_transition", 
                default="Select the transition you want to use when an image is being added(only for classic gallery)."
            )
        ),
        vocabulary=TRANSITIONS,
        default="fade",
        enforceVocabulary = True,
        schemata="advanced"
    ),
    StringField(
        name="slideshowEffect",
        widget=SelectionWidget(
            label=_(u"label_slideshowEffect", default=u"Slideshow Effect"),
            description=_(u"description_slideshowEffect", 
                default="Select the effect you want to use(only for Slideshow 2 gallery)."
            )
        ),
        vocabulary=(
            ('flash:Slideshow.Flash', _(u"label_slideshowEffect_flash", default=u"Flash")),
            ('fold:Slideshow.Fold', _(u"label_slideshowEffect_fold", default=u"Fold")),
            ('kenburns:Slideshow.KenBurns', _(u"label_slideshowEffect_kenburns", default=u"Ken Burns")),
            ('push:Slideshow.Push', _(u"label_slideshowEffect_push", default=u"Push")),
            (':Slideshow', _(u"label_slideshowEffect_none", default=u"none"))
        ),
        default="kenburns:Slideshow.KenBurns",
        enforceVocabulary = True,
        schemata="advanced"
    )
    )
)


GallerySchema = ATFolderSchema.copy() + schema.copy()

#remove extra schematas
for field in GallerySchema.fields():
    okay_schematas = [t.name for t in GalleryTypes]
    okay_schematas.extend(['advanced'])
    
    if field.schemata not in okay_schematas:
        field.schemata = "metadata"

class Gallery(ATFolder):
    """A folder which can contain other items."""
    implements(IGallery)

    schema         =  GallerySchema

    portal_type    = 'Gallery'
    archetype_name = 'Gallery'
    _atct_newTypeFor = {'portal_type' : 'CMF Folder', 'meta_type' : 'Plone Folder'}

    __implements__ = (ATFolder.__implements__,)

    security       = ClassSecurityInfo()
    
    contains_sub_gallery_objects = False
    last_cooked_time_in_minutes = 0
    cooked_images = []
        
    def containsSubGalleries(self):
        return self.contains_sub_gallery_objects
        
    def galleries(self):
        return [g.getObject() for g in self.getFolderContents() if g.meta_type == "Gallery"]

    def get_gallery_types_vocabulary(self):
        vocab = []
        for t in GalleryTypes:
            vocab.append([t.name, t.description])

        return vocab
        
        
    def get_display_types_vocabulary(self):
        from collective.plonetruegallery.meta.zcml import DisplayTypes
        vocab = []
        for t in DisplayTypes:
            vocab.append([t.name, t.description])

        return vocab

registerATCT(Gallery, PROJECTNAME)