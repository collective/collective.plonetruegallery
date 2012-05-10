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


class IFlickrAdapter(IGalleryAdapter):
    """
    """

    flickr = Attribute("returns a flickrapi object for the api key")

    def get_flickr_user_id(username):
        """
        Returns the actual user id of someone given a username.
        if a username is not given, it will use the one in its
        settings
        """

    def get_flickr_photoset_id(theset=None, userid=None):
        """
        Returns the photoset id given a set name and user id.
        Uses the set and get_flickr_user_id() if they are
        not specified.
        """

    def get_mini_photo_url(photo):
        """
        takes a photo and creates the thumbnail photo url
        """

    def get_photo_link(photo):
        """
        creates the photo link url
        """

    def get_large_photo_url(photo):
        """
        create the large photo url
        """


class IPicasaAdapter(IGalleryAdapter):
    """
    """

    gd_client = Attribute("property for gd_client instance")

    def get_album_name(name, user):
        """
        Returns the selected album name and user.
        Uses name and user in settings if not specified.
        """

    def feed():
        """
        Returns the picasa feed for the given album.
        """


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
                    u"have different size constraints."),
        default='medium',
        vocabulary=SimpleVocabulary([
            SimpleTerm('small', 'small', _(u"label_size_small",
                                            default=u'Small')),
            SimpleTerm('medium', 'medium', _(u"label_size_medium",
                                            default=u'Medium')),
            SimpleTerm('large', 'large', _(u"label_size_large",
                                            default=u'Large'))
        ]))
    thumb_size = schema.Choice(
        title=_(u"label_thumb_size", default=u"Thumbnail image size"),
        description=_(u"description_thumb_size",
            default=u"The size of thumbnail images. "
                    u"Will only work with plone image gallery type."
        ),
        default='thumb',
        vocabulary=SimpleVocabulary([
            SimpleTerm('tile', 'tile', _(u"label_tile", default=u"tile")),
            SimpleTerm('thumb', 'thumb', _(u"label_thumb", default=u"thumb")),
            SimpleTerm('mini', 'mini', _(u"label_mini", default=u"mini")),
            SimpleTerm('preview', 'preview', _(u"label_preview",
                                                default=u"preview")),
        ]))
    # the options for the display type will also be added dynamically
    timed = schema.Bool(
        title=_(u"label_timed", default=u"Timed?"),
        description=_(u"description_timed",
            default=u"Should this gallery automatically "
                    u"change images for the user?"
        ),
        default=True)
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
    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"Batch Size"),
        description=_(u"description_batch_size",
            default=u"The amount of images shown in one page. "
                    u"This is not used for all display types."
        ),
        default=50,
        required=True)


class IBaseSettings(Interface):
    pass


class IFancyBoxDisplaySettings(IBaseSettings):
    pass


class IHighSlideDisplaySettings(IBaseSettings):
    highslide_slideshowcontrols_position = schema.Choice(
        title=_(u"lable_highslide_slideshowcontrols_position",
            default=u"Highslide controls position"),
        description=_(u"description_highslide_slideshowcontrols_position",
            default=u"Choose the position of the slideshow controls. "
        ),
        default='bottom',
        vocabulary=SimpleVocabulary([
            SimpleTerm('top', 'top',
                _(u"label_highslide_slideshowcontrols_position_top",
                                    default=u"top")),
            SimpleTerm('middle', 'middle',
                _(u"label_highslide_slideshowcontrols_position_middle",
                                    default=u"middle")),
            SimpleTerm('bottom', 'bottom',
                _(u"label_highslide_slideshowcontrols_position_bottom",
                                    default=u"bottom")),
        ]))
    highslide_outlineType = schema.Choice(
        title=_(u"label_highslide_outlineType", default=u"Image outline type"),
        description=_(u"description_highslide_outlineType",
            default=u"The style of the border around the image. "
        ),
        default='drop-shadow',
        vocabulary=SimpleVocabulary([
            SimpleTerm('rounded-white', 'rounded-white',
                _(u"label_highslide_outlineType_rounded_white",
                                    default=u"Rounded White")),
            SimpleTerm('outer-glow', 'outer-glow',
                _(u"label_highslide_outlineType_outer_glow",
                                    default=u"Outer Glow")),
            SimpleTerm('drop-shadow', 'drop-shadow',
                _(u"label_highslide_outlineType_drop_shadow",
                                    default=u"Drop Shadow")),
            SimpleTerm('glossy-dark', 'glossy-dark',
                _(u"label_highslide_outlineType_glossy_dark",
                                    default=u"Glossy Dark")
            )
        ]))


class IGallerifficDisplaySettings(IBaseSettings):
    gallerific_style = schema.Choice(
        title=_(u"label_gallerific-style", default=u"Layout"),
        description=_(u"description_gallerific-style",
            default=u"The style of the Galleriffic layout. "
        ),
        default='style.css',
        vocabulary=SimpleVocabulary([
            SimpleTerm('style.css', 'style.css',
                _(u"label_gallerific_style",
                                    default=u"Default Layout")),
            SimpleTerm('style2.css', 'style2.css',
                _(u"label_gallerific_style2",
                                    default=u"Linklayout")
            )
        ]))


class IS3sliderDisplaySettings(IBaseSettings):
    s3_width = schema.TextLine(
        title=_(u"label_s3_width",
            default=u"Width of the gallery"),
        default=u"600px")
    s3_height = schema.TextLine(
        title=_(u"label_s3_height",
            default=u"Height of the gallery"),
        default=u"350px")
    s3_textwidth = schema.TextLine(
        title=_(u"label_s3_textwidth",
            default=u"Width of the (black) text box"),
        default=u"150px")


class INivosliderDisplaySettings(IBaseSettings):
    nivoslider_width = schema.Int(
        title=_(u"label_nivoslider_width",
            default=u"Width of the gallery in pixels"),
        default=600)
    nivoslider_height = schema.Int(
        title=_(u"label_nivoslider_height",
            default=u"Height of the gallery in pixels"),
        default=350)
    nivoslider_theme = schema.Choice(
        title=_(u"nivoslider_theme", default=u"Nivoslider Theme"),
        default=u"default",
        vocabulary=SimpleVocabulary([
            SimpleTerm("default", "default",
                _(u"label_nivoslider_theme1", default=u"Default Theme")),
            SimpleTerm("orman", "orman",
                _(u"label_nivoslider_theme2", default=u"Orman Theme")),
            SimpleTerm("pascal", "pascal",
                _(u"label_nivoslider_theme3", default=u"Pascal Theme")),
            SimpleTerm("oldframe", "oldframe",
                _(u"label_nivoslider_theme4", default=u"Old Frame Theme")),
            SimpleTerm("overlay", "overlay",
                _(u"label_nivoslider_theme5", default=u"Overlay Theme")),
            SimpleTerm("bendit", "bendit",
                _(u"label_nivoslider_theme6", default=u"Bendit Theme")),
            SimpleTerm("tv", "tv",
                _(u"label_nivoslider_theme7", default=u"TV Theme")),
            SimpleTerm("thumbnail", "thumbnail",
                _(u"label_nivoslider_theme8", default=u"Thumbnail Theme")
            )
        ]))
    nivoslider_effect = schema.Choice(
        title=_(u"label_nivoslider_effect", default=u"Transition Effect"),
        default='random',
        vocabulary=SimpleVocabulary([
            SimpleTerm('fold', 'fold',
                _(u"label_nivoslider_effect1", default=u"Fold")),
            SimpleTerm('fade', 'fade',
                _(u"label_nivoslider_effect2", default=u"Fade")),
            SimpleTerm('sliceDown', 'sliceDown',
                _(u"label_nivoslider_effect3", default=u"Slice Down")),
            SimpleTerm('sliceDownLeft', 'sliceDownLeft',
                _(u"label_nivoslider_effect3", default=u"Slice Down Left")),
            SimpleTerm('sliceUp', 'sliceUp',
                _(u"label_nivoslider_effect4", default=u"Slice Up")),
            SimpleTerm('sliceUpLeft', 'sliceUpLeft',
                _(u"label_nivoslider_effect5", default=u"Slice Up Left")),
            SimpleTerm('sliceUpDown', 'sliceUpDown',
                _(u"label_nivoslider_effect6", default=u"Slice Up Down")),
            SimpleTerm('sliceUpDownLeft', 'sliceUpDownLeft',
                _(u"label_nivoslider_effect7", default=u"Slice Up Down Left")),
            SimpleTerm('sliceInRight', 'sliceInRight',
                _(u"label_nivoslider_effect8", default=u"Slide In Right")),
            SimpleTerm('slideInLeft', 'slideInLeft',
                _(u"label_nivoslider_effect9", default=u"Slide In Left")),
            SimpleTerm('boxRain', 'boxRain',
                _(u"label_nivoslider_effect10", default=u"Box Rain")),
            SimpleTerm('boxRainReverse', 'boxRainReverse',
                _(u"label_nivoslider_effect11", default=u"Box Rain Reverse")),
            SimpleTerm('boxRandom', 'boxRandom',
                _(u"label_nivoslider_effect12", default=u"Box Random")),
            SimpleTerm('boxRainGrow', 'boxRainGrow',
                _(u"label_nivoslider_effect13", default=u"Box Rain Grow")),
            SimpleTerm('boxRainGrowReverse', 'boxRainGrowReverse',
                _(u"label_nivoslider_effect14",
                        default=u"box Rain Grow Reverse")),
            SimpleTerm('random', 'random',
                _(u"label_nivoslider_effect15", default=u"Random")
            )
        ]))
    nivoslider_randomstart = schema.Bool(
        title=_(u"label_nivoslider_randomstart",
            default=u"Start on random image?"),
        default=False)
    nivoslider_directionnav = schema.Bool(
        title=_(u"label_nivoslider_r_directionnar",
            default=u"Next & Prev navigation??"),
        default=False)
    nivoslider_directionnavhide = schema.Bool(
        title=_(u"label_nivoslider_directionnavhide",
            default=u"Only show Next & Prev on hover"),
        default=True)
    nivoslider_pauseonhover = schema.Bool(
        title=_(u"label_nivoslider_pauseonhover",
            default=u"Stop animation while hovering?"),
        default=False)
    nivoslider_slices = schema.Int(
        title=_(u"label_nivoslider_slices",
            default=u"Nuber of slices, for slice animations"),
        default=15)
    nivoslider_boxcols = schema.Int(
        title=_(u"label_nivoslider_boxcols",
            default=u"Number of columns for box animations"),
        default=8)
    nivoslider_boxrows = schema.Int(
        title=_(u"label_nivoslider_boxrows",
            default=u"Number of rows for box animations"),
        default=4)


class INivogalleryDisplaySettings(IBaseSettings):
    nivogallery_directionnav = schema.Bool(
        title=_(u"label_nivogallery_directionnav",
            default=u"Show navigation arrows on the image"),
        default=True)
    nivogallery_progressbar = schema.Bool(
        title=_(u"label_nivogallery_progressbar",
            default=u"Show progressbar at the top"),
        default=True)
    nivogallery_width = schema.TextLine(
        title=_(u"label_nivogallery_width",
            default=u"Width of the gallery"),
        default=u"600px")
    nivogallery_height = schema.TextLine(
        title=_(u"label_nivogallery_height",
            default=u"Height of the gallery. You can not set the height in %"),
        default=u"350px")


class IPikachooseDisplaySettings(IBaseSettings):
    pikachoose_width = schema.Int(
        title=_(u"label_pikachoose_width",
            default=u"Width of the gallery in pixels"),
        default=600,
        min=10)
    pikachoose_height = schema.Int(
        title=_(u"label_pikachoose_height",
            default=u"Height of the gallery in pixels"),
        default=350,
        min=10)
    pikachoose_backgroundcolor = schema.Choice(
        title=_(u"label_pikachoose_backgroundcolor",
                default=u"backgroundcolor"),
        default='222',
        vocabulary=SimpleVocabulary([
            SimpleTerm('222', '222',
                _(u"label_backgroundcolors", default=u"Dark")),
            SimpleTerm('DDD', 'DDD',
                _(u"label_backgroundcolors2", default=u"Grey")),
            SimpleTerm('f6f6f6', 'f6f6f6',
                _(u"label_backgroundcolors3", default=u"Offwhite")),
            SimpleTerm('FFF', 'FFF',
                _(u"label_backgroundcolors4", default=u"White")
            )
        ]))
    pikachoose_showtooltips = schema.Bool(
        title=_(u"label_pikachoose_tooltip", default=u"Show tooltip"),
        default=False)
    pikachoose_showcaption = schema.Bool(
        title=_(u"label_pikachoose_caption", default=u"Show caption"),
        default=True)
    pikachoose_vertical = schema.Bool(
        title=_(u"label_pikachoose_vertical", default=u"Vertical"),
        default=False)
    pikachoose_transition = schema.Choice(
        title=_(u"label_pikachoose_transition", default=u"Transition"),
        default=4,
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, 1,
                _(u"label_transitions", default=u"Full frame cross fade")),
            SimpleTerm(2, 2,
                _(u"label_transitions2", default=u"Paneled fold out")),
            SimpleTerm(3, 3,
                _(u"label_transitions3", default=u"Horizontal blinds")),
            SimpleTerm(4, 4,
                _(u"label_transitions4", default=u"Vertical blinds")),
            SimpleTerm(5, 5,
                _(u"label_transitions5", default=u"Small box random fades")),
            SimpleTerm(6, 6,
                _(u"label_transitions6", default=u"Full image blind slide")),
            SimpleTerm(0, 0,
                _(u"label_transitions7", default=u"Fade out then fade in")
            )
        ]))


class IGalleriaDisplaySettings(IBaseSettings):
    galleria_theme = schema.Choice(
        title=_(u"galleria_theme_title", default=u"Theme"),
        default='light',
        vocabulary=SimpleVocabulary([
            SimpleTerm('dark', 'dark', _(u"label_dark", default=u"Dark")),
            SimpleTerm('light', 'light', _(u"label_light", default=u"Light")),
            SimpleTerm('classic', 'classic', _(u"label_classic",
                                               default=u"Classic"))
        ]))
    galleria_transition = schema.Choice(
        title=_(u"galleria_transition", default=u"Transition"),
        default='fadeslide',
        vocabulary=SimpleVocabulary([
            SimpleTerm('fadeslide', 'fadeslide', _(u"label_fadeslide",
                default=u"Fade Slide - fade between images and "
                        u"slide slightly at the same time")),
            SimpleTerm('fade', 'fade', _(u"label_fade",
                default=u"Fade - crossfade betweens images")),
            SimpleTerm('flash', 'flash', _(u"label_flash",
                default=u"Flash - fades into background color "
                        u"between images")),
            SimpleTerm('pulse', 'pulse', _(u"label_pulse",
                default=u"Pulse - quickly removes the image into background "
                        u"color, then fades the next image")),
            SimpleTerm('slide', 'slide', _(u"label_slide",
                default=u"Slide - slides the images depending on image "
                        u"position"))
        ]))
    galleria_auto_show_info = schema.Bool(
        title=_(u'galleria_label_auto_show_info', default="Auto show info"),
        description=_(u'galleria_desc_auto_show_info',
            default="start gallery out with info showing"),
        default=True)


class IContactsheetDisplaySettings(IBaseSettings):
    contactsheet_columns = schema.Int(
        title=_(u"label_contactsheet_columns",
            default=u"Number of images before a forced new row (use a high "
                    u"number if you dont want this)"),
        default=3,
        min=1)
    contactsheet_imagewidth = schema.Int(
        title=_(u"label_contactsheet_imagewidth",
            default=u"Width of (each) image box"),
        default=400,
        min=50)
    contactsheet_imageheight = schema.Int(
        title=_(u"label_contactsheet_imageheight",
            default=u"Height of (each) image box"),
        default=260,
        min=50)
    contactsheet_overlay_opacity = schema.Choice(
        title=_(u"label_contactsheet_overlay_opacity",
                default=u"Opacity on mouse over"),
        default=0.3,
        vocabulary=SimpleVocabulary([
            SimpleTerm(0.1, 0.1,
                _(u"label_contactsheet_overlay_opacity1",
                    default=u"0.1 Light")),
            SimpleTerm(0.2, 0.2,
                _(u"label_contactsheet_overlay_opacity2", default=u"0.2")),
            SimpleTerm(0.3, 0.3,
                _(u"label_contactsheet_overlay_opacity3", default=u"0.3")),
            SimpleTerm(0.4, 0.4,
                _(u"label_contactsheet_overlay_opacity4",
                    default=u"0.4 Medium")),
            SimpleTerm(0.5, 0.5,
                _(u"label_contactsheet_overlay_opacity5", default=u"0.5")),
            SimpleTerm(0.6, 0.6,
                _(u"label_contactsheet_overlay_opacity6",
                    default=u"0.6")),
            SimpleTerm(0.7, 0.7,
                _(u"label_contactsheet_overlay_opacity7",
                    default=u"0.7 Dark")),
            SimpleTerm(0.8, 0.8,
                _(u"label_contactsheet_overlay_opacity8",
                    default=u"0.8 Very Dark")),
            SimpleTerm(0.9, 0.9,
                _(u"label_contactsheet_overlay_opacity9",
                    default=u"0.9 Almost Black")
            )
        ]))


class IThumbnailzoomDisplaySettings(IBaseSettings):
    thumbnailzoom_columns = schema.Int(
        title=_(u"label_thumbnailzoom_columns",
            default=u"Number of thumbs before a forced new row (use a high "
                    u"number if you dont want this)"),
        default=3,
        min=1)
    thumbnailzoom_increase = schema.Int(
        title=_(u"label_thumbnailzoom_increase",
            default=u"Pixels to zoom when mouse over"),
        default=50)
    thumbnailzoom_effectduration = schema.Int(
        title=_(u"label_thumbnaizoom_effectduration",
            default=u"How long time the effect takes"),
        default=100,
        min=16)


class IPresentationDisplaySettings(IBaseSettings):
    presentation_effect = schema.Choice(
        title=_(u"label_presentation_effect",
            default=u"Mouseover or click"),
        default="click",
        vocabulary=SimpleVocabulary([
            SimpleTerm("click", "click",
                _(u"label_presentation_click", default=u"Click on image")),
            SimpleTerm("mouseenter", "mouseenter",
                _(u"label_presentation_mouseover", default=u"Mouse enter")
            )
        ]))
    presentation_width = schema.Int(
        title=_(u"label_presentation_width",
            default=u"Width of the gallery in pixels"),
        default=600,
        min=200)
    presentation_height = schema.Int(
        title=_(u"label_presentation_height",
            default=u"Height of the gallery in pixels"),
        default=350,
        min=60)
    minimum_width = schema.Int(
        title=_(u"label_presentation_minimum_width",
            default=u"Minimum width of images"),
        default=15)
    presentation_xposition = schema.Choice(
        title=_(u"label_presentation_xposition",
            default=u"Horizontal image position"),
        default="center",
        vocabulary=SimpleVocabulary([
            SimpleTerm("top", "top",
                _(u"label_presentation_xpositiontop", default=u"Top")),
            SimpleTerm("center", "center",
                _(u"label_presentation_xpositioncenter", default=u"Center")),
            SimpleTerm("bottom", "bottom",
                _(u"label_presentation_xpositionbottom", default=u"Bottom")
            )
        ]))
    presentation_yposition = schema.Choice(
        title=_(u"label_presentation_yposition",
            default=u"Vertical image position"),
        default="center",
        vocabulary=SimpleVocabulary([
            SimpleTerm("left", "left",
                _(u"label_presentation_ypositionleft", default=u"Left")),
            SimpleTerm("center", "center",
                _(u"label_presentation_ypositioncenter", default=u"Center")),
            SimpleTerm("right", "right",
                _(u"label_presentation_ypositionright", default=u"Right")
            )
        ]))


class IContentFlowSettings(IBaseSettings):
    flow_addons = schema.Tuple(
        title=_(u"label_contentflow_addons", default="Addons"),
        missing_value=None,
        default=("white",),
        required=False,
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary([
                SimpleTerm("white", "white",
                    _(u"label_content_flow_addon_white", default=u"White")),
                SimpleTerm("black", "black",
                    _(u"label_content_flow_addon_black", default=u"Black")),
                SimpleTerm("gallery", "gallery",
                    _(u"label_content_flow_addon_gallery",
                        default=u"Gallery")),
                SimpleTerm("roundabout", "roundabout",
                    _(u"label_content_flow_addon_roundabout",
                        default=u"Roundabout")),
                SimpleTerm("screwdriver", "screwdriver",
                    _(u"label_content_flow_addon_screwdriver",
                        default=u"Screwdriver")),
                SimpleTerm("slideshow", "slideshow",
                    _(u"label_content_flow_addon_slideshow",
                        default=u"Slideshow"))
            ])))
    flow_max_image_height = schema.Int(
        title=_(u"label_contentflow_image_height",
            default="Max Image Height"),
        description=_(u"desc_contentflow_image_height",
            default=u"Customize how large the image shows. If zero, "
                    u"a best guess height will be selected based on the"
                    u"width. This is translated to pixels."),
        default=0,
        required=True)


class IBasicGallerySettings(IBaseSettings):
    pass


class IFlickrGallerySettings(IBaseSettings):
    flickr_username = schema.TextLine(
        title=_(u"label_flickr_username", default=u"flickr username"),
        description=_(u"description_flickr_username",
            default=u"The username/id of your flickr account. "
                    u"(*flickr* gallery type)"
        ),
        required=False)
    flickr_set = schema.TextLine(
        title=_(u"label_flickr_set", default="Flickr Set"),
        description=_(u"description_flickr_set",
            default=u"Name/id of your flickr set."
                    u"(*flickr* gallery type)"
        ),
        required=False)


class IPicasaGallerySettings(IBaseSettings):
    picasa_username = schema.TextLine(
        title=_(u"label_picasa_username", default=u"GMail address"),
        description=_(u"description_picasa_username",
            default=u"GMail address of who this album belongs to. "
                    u"(*Picasa* gallery type)"
        ),
        required=False)
    picasa_album = schema.TextLine(
        title=_(u"label_picasa_album", default=u"Picasa Album"),
        description=_(u"description_picasa_album",
            default=u"Name of your picasa web album. "
                    u"This will be the qualified name you'll see in "
                    u"the address bar or the full length name of the "
                    u"album. (*Picasa* gallery type)"
        ),
        required=False)


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
        """
