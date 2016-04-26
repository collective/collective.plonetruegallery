from zope.interface import Interface, Attribute
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery import PTGMessageFactory as _


class IGalleryAdapter(Interface):
    sizes = Attribute("image size mappings for the gallery type")
    schema = Attribute("Schema of gallery specific")
    name = Attribute("Name of the gallery")
    description = Attribute("Description of gallery type")
    cook_delay = Attribute("Time between updates of gallery images.  "
        "This update of images can be forced by appending refresh on "
        "a gallery.")
    cooked_images = Attribute("The images after they've been cooked up.")

    def cook():
        """
        this will make it so the gallery's images are not aggregated every
        single time the gallery is displayed.
        """

    def time_to_cook():
        """
        called to see if it is time to the cook the gallery.
        """

    def get_random_image():
        """
        returns a random image with data.
        returns an empty dict if the gallery is empty.
        """

    def get_first_image():
        """
        returns the first image with data.
        returns an empty dict if the gallery is empty.
        """

    def log_error():
        """
        provides an easy way to log errors in gallery adapters.
        we don't want an adapter to prevent a page from loading...
        Who knows what kind of odd behavior some adapters may run into
        when working with picasa or flickr apis...
        """

    def retrieve_images():
        """
        This method retrieves all the images to be cooked
        """
    def number_of_images():
        """"""

    def get_all_images():
        """
        returns all the cooked images for the gallery
        """


class IBasicAdapter(IGalleryAdapter):
    """
    Use plone to manage images for the gallery.
    """

    size_map = Attribute("allows us to map specific sizes to plone urls")



class IDisplayType(Interface):
    name = Attribute("name of display type")
    description = Attribute("description of type")
    schema = Attribute("Options for this display type")
    userWarning = Attribute("A warning to be displayed to to "
                            "the user if they use this type.")
    width = Attribute("The width of the gallery")
    height = Attribute("The height of the gallery")
    start_image_index = Attribute("What image the gallery should "
                                  "start playing at.")

    def content():
        """
        the content of the display yet
        """

    def javascript():
        """
        content to be included in javascript area of template
        """

    def css():
        """
        content to be included in css area of template
        """


class IBatchingDisplayType(Interface):

    def uses_start_image(self):
        """
        disable start image if a batch start is specified.
        """

    b_start = Attribute("")
    start_image_index = Attribute("")

    def get_page(self):
        """"""

    start_automatically = Attribute("")
    batch = Attribute("")


class IGallery(Interface):
    """
    marker interface for content types that implement
    the gallery
    """


class IGallerySettings(Interface):
    gallery_type = schema.Choice(
        title=_(u"label_gallery_type", default=u"Type"),
        description=_(u"description_gallery_type",
            default=u"Select the type of gallery you want this to be.  "
                    u"If you select something other than default, you "
                    u"must fill out the information in the corresponding "
                    u"tab for that gallery type."),
        vocabulary="collective.plonetruegallery.GalleryTypeVocabulary",
        default="basic")
    display_type = schema.Choice(
        title=_(u"label_gallery_display_type",
                default=u"Gallery Display Type"),
        description=_(
            u"label_gallery_display_type_description",
            default=u"Choose the method in which the "
                    u"gallery should be displayed"
        ),
        default="galleria",
        vocabulary="collective.plonetruegallery.DisplayTypes")
    # the specific options for the gallery types will be added
    # dynamcially in the form
    size = schema.Choice(
        title=_(u"label_gallery_size", default=u"Size"),
        description=_(u"description_gallery_size",
            default=u"The actual sizes used can vary depending on the "
                    u"gallery type that is used since different services "
                    u"have different size constraints. "
                    u"Only 'Small, Medium and Large' work with Flickr and Picasa"),
        default='large',
        vocabulary="collective.plonetruegallery.SizeVocabulary",
        )
    thumb_size = schema.Choice(
        title=_(u"label_thumb_size", default=u"Thumbnail image size"),
        description=_(u"description_thumb_size",
            default=u"The size of thumbnail images. "
                    u"Will only work with plone image gallery type."
        ),
        default='thumb',
        vocabulary="collective.plonetruegallery.ThumbVocabulary",
        )
    # the options for the display type will also be added dynamically
    timed = schema.Bool(
        title=_(u"label_timed", default=u"Timed?"),
        description=_(u"description_timed",
            default=u"Should this gallery automatically "
                    u"change images for the user?"
        ),
        default=True)
    copyright = schema.Bool(
        title=_(u"label_copyright", default=u"Copyright notice?"),
        description=_(u"description_copyright",
            default=u"Should copyright notices be attached "
                    u"to each image?"
        ),
        default=False)
    delay = schema.Int(
        title=_(u"label_delay", default=u"Delay"),
        description=_(u"description_delay",
            default=u"If slide show is timed, the delay sets "
                    u"how long before the next image is shown in miliseconds."
        ),
        default=5000,
        required=True)
    duration = schema.Int(
        title=_(u"label_image_change_duration", default=u"Change Duration"),
        description=_(u"description_fade_in_duration",
            default=u"The amount of time the change effect should "
                    u"take in miliseconds."
        ),
        default=500,
        required=True)
    show_subgalleries = schema.Bool(
        title=_(u"label_show_subgalleries", default=u"Show Sub-Galleries?"),
        description=_(u"description_show_subgalleries",
            default=u"If you select this option, previews for all "
                    u"nested galleries will show up below this gallery."
        ),
        default=True)
    random_subgallery_lead = schema.Bool(
        title=_(u"label_random_subgallery_lead", default=u"Show random lead image for subgalleries?"),
        description=_(u"desciption_random_subgallery_lead",
            default=u"If you select this option, the lead images for the subgalleries will be chosen at random. "
                u"Otherwise the first image is chosen."
        ),
        default=True)
    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"Batch Size"),
        description=_(u"description_batch_size",
            default=u"The amount of images shown in one page. "
                    u"This is not used for all display types."
        ),
        default=50,
        required=True)
    enable_bodytext = schema.Bool(
        title=_(u"label_enable_bodytext", default=u"Enable bodytext"),
        description=_(u"description_bodytext",
            default=u"This is only used for customized templates to show body text"
        ),
        default=False)
    custom_stylesheet = schema.TextLine(
        title=_(u"label_custom_stylesheet", default=u"Custom stylesheet"),
        description=_(u"description_custom_stylesheet",
            default=u"Relative path from the root of the site where the stylesheet "
                    u"will be referenced from. This will be included after the display "
                    u"gallery type's styles and is a good entry point for customization."
        ),
        default=u"",
        required=False)


class IBaseSettings(Interface):
    pass


class IBasicGallerySettings(IBaseSettings):
    pass


class IImageInformationRetriever(Interface):
    """
    This interface is interesting for everybody who wants to filter
    the items to be shown in a gallery view
    """
    def getImageInformation(self, size):
        """
        Return a list of Information relevant for gallery display for each
        image.
        Size should be a hint of the image size to use, in string format.
        The standard implementations support the following sizes, which
        map to the given size of the archetypes Image size:

            small -> mini
            medium -> preview
            large -> large

        This information returned consists of:
        image_url
            The URL to the image itself
        thumb_url
            The URL to a thumbnail version of the image
        link
            The Link to which an image must point to
        title
            The image title
        description
            The image description
        copyright
            The image copyright
        keywords'
            image tags
        bodytext
            the body text (html)
        """
