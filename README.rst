collective.plonetruegallery Documentation
=========================================

.. image:: https://secure.travis-ci.org/collective/collective.plonetruegallery.png
    :target: http://travis-ci.org/#!/collective/collective.plonetruegallery

Introduction
------------
collective.plonetruegallery is a Plone add-on that implements a very
customizable and sophisticated gallery.


Plone Version Compatibility
---------------------------

Works with Plone 5.0 and earlier.


How It Works
------------
collective.plonetruegallery adds a ``Gallery View`` to Folders and Collections.

For any Folder or Collection containing or showing images, use the
Display toolbar menu and select ``Gallery View``.

Once that is done, a ``Gallery Settings`` toolbar menu is enabled for
the type. With this, you can customize the various settings for the
Gallery.

.. image:: https://raw.githubusercontent.com/collective/collective.plonetruegallery/master/docs/collective.plonetruegallery-screenshot-01.jpg
.. image:: https://raw.githubusercontent.com/collective/collective.plonetruegallery/master/docs/collective.plonetruegallery-screenshot-02.jpg
.. image:: https://raw.githubusercontent.com/collective/collective.plonetruegallery/master/docs/collective.plonetruegallery-screenshot-03.jpg
.. image:: https://raw.githubusercontent.com/collective/collective.plonetruegallery/master/docs/collective.plonetruegallery-screenshot-04.jpg


Supported Display Types
-----------------------

To install any of the various extra display types, you need to install
the dependent package in buildout

- galleria (included in default installation of collective.plonetruegallery)
- contact sheet (collective.ptg.contactsheet)
- thumbnail zoom gallery (collective.ptg.thumbnailzoom)
- presentation (collective.ptg.presentation)
- galleriffic (collective.ptg.galleriffic)
- highslide (collective.ptg.highslide)
- fancybox (collective.ptg.fancybox)
- pikachoose (collective.ptg.pikachoose)
- s3slider (collective.ptg.s3slider)
- nivo slider (collective.ptg.nivoslider)
- nivo gallery (collective.ptg.nivogallery)
- content flow (collective.ptg.contentflow)
- supersized (collective.ptg.supersized)

Buildout configuration
~~~~~~~~~~~~~~~~~~~~~~
::

  eggs = 
    ...
    collective.plonetruegallery
    collective.ptg.highslide
    collective.ptg.fancybox
    collective.ptg.galleriffic
    collective.ptg.s3slider
    collective.ptg.pikachoose
    collective.ptg.nivoslider
    collective.ptg.nivogallery
    collective.ptg.contentflow
    collective.ptg.supersized
    collective.ptg.thumbnailzoom
    collective.ptg.contactsheet
    ...


Installing all galleries
~~~~~~~~~~~~~~~~~~~~~~~~

If you want to install all available galleries, you could add
::

  eggs = 
    ...
    collective.plonetruegallery
    collective.ptg.allnewest
    ...

to buildout's egg section.

This will also install some galleries that are "under development".



Features
--------
* Flickr and Picasa Support!
* Dexterity "Lead Image behaviour" support
* Works with 'Image', 'News Item' and other content types that has a Image Field (provides IImageContent). 
* Also works with redturtle.smartlink and collective.contentleadimage (install http://pypi.python.org/pypi/collective.ptg.contentleadimage )
* Customize gallery size, transition(limited transitions right now), timed and
  other settings
* Can use nested galleries
* searching and category selection for nested galleries
* Galleria, Galleriffic, Highslide JS, s3slider, Pikachoose and Fancybox display types
* display gallery inline
* Products.Collage integration
* Compatible with new-style Plone collections
* Provides base settings configlet


Flickr and Picasa Web Album Support
-----------------------------------
* to add support for these type of galleries you must install additional
  packages
* install collective.ptg.flickr for Flickr support
* install collective.ptg.picasa for Picasa Web Album
  Support(tested with 1.3.3 and 2.0.12)
* on Plone 3.x you must also manually install hashlib for picasa support
* these can just be added to your buildout or installed with easy_install
  or you can add the package to your egg section like


Displaying Gallery inline
-------------------------
A view (@@placegalleryview) can be used to place the gallery inside of
other content.

Pop-up effect
-------------

you could do this::

  1) Install http://plone.org/products/collective.prettyphoto
  2) Mark the link to the gallery with "prettyPhoto" style (which 
     has now been added) from Kupu or TinyMCE

Inline Gallery
--------------

For showing a gallery in another page, try something like this::

  <object data="path/to/gallery/@@placegalleryview" height="400" width="500">
    <param name="data" value="path/to/gallery" />
  </object>

Notes for successful inline object tag usage:

* You will have to "whitelist" <object> and <param> in portal_transform safe-html.
* When editing in Plone 4.2 you will have to switch your editor to Kupu since TinyMCE fracks up the object tag into a flash item. 
* If testing without Apache in front of your Plone you will need to make sure that the
  "path/to/gallery" path from the example above includes any levels above the Plone object
  in the Zope instance (eg. if your Plone object is inside of a folder named "version1", and
  the name of your gallery is "mygallery", then the path should read "/version1/Plone/mygallery".
  Of course, you will need to remove the "/version1/Plone" part when you put Apache in front
  of your Plone.

Or you can do the same with an iframe

Re-use gallery in page template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to place the gallery in another page template, you can re-use the entire HTML as-is::

  <tal:gallery tal:replace="structure context/fotos/@@placegalleryview" />

This has the advantage, over <object> embedding, that a modal (pop-up) showing the enlarged image will take up the entire screen, instead of just the <object> area.

Troubleshooting safe-html
-------------------------

If you have trouble, do this:
Go to safe_html in portal_transforms tool
Make sure param and object are valid tags (not nasty tag).

After that, you should flush the cache of ZODB by going to
1. Zope root app ZMI
2. Control Panel
3. Database
4. main (or whatever zodb you have)
5. Flush Cache tab
6. Press "Minimize" button

This will remove from ZODB cache all cooked texts. This procedure is mentioned
at the top of safe_html in portal_transforms.


Upgrading
---------

From 0.8*
~~~~~~~~~
The upgrade to version 0.8* is an important and large update. Basically, it
gets rid of the Gallery type, replaces it with the regular Folder type along
with a new view applied to the folder, namely the "Gallery View."

You can only successfully upgrade from the 0.8* series by first upgrading
to a 1.x series release and then upgrading to the 2.x series.


From 1.x to 2.x
~~~~~~~~~~~~~~~

No longer support Slideshow 2 gallery which has been replaced with galleria.

From * to 3.x
~~~~~~~~~~~~~

You'll be required to change your respective collective.js dependencies to
collective.ptg dependencies in buildout, re-run buildout.


Installation
------------
Since this product depends on plone.app.z3cform, you'll need to add a few
overrides for products versions in your buildout if you aren't using recent
versions of Plone. Good news is that is you're using any other product that
uses plone.app.z3cform, you'll already be good to go.

Basically, you'll need to add these to your buildout versions section
ONLY IF you're running a plone < 4.1.

For Plone 4.0::

  [versions]
  z3c.form = 2.3.2
  plone.app.z3cform = 0.5.0
  plone.z3cform = 0.6.0
  zope.schema = 3.6.0


and Plone 3.x::

  [versions]
  z3c.form = 1.9.0
  plone.app.z3cform = 0.4.8
  plone.z3cform = 0.5.10
  zope.i18n = 3.4.0
  zope.testing = 3.4.0
  zope.component = 3.4.0
  zope.securitypolicy = 3.4.0
  zope.app.zcmlfiles = 3.4.3


These versions are not the exact versions plonetruegallery requires, it's
just a known working set. If you already have plone.app.z3cform installed
under different versions or wish to upgrade versions, you're fine doing so.


Then once you run buildout with this configuration, install
collective.plonetruegallery via the the add-on product configuration. Also,
make sure Plone z3cform support is installed too. If you experience issues
where no settings appear in the `Gallery Settings` tab,
reinstall `Plone z3cform support`.

Uninstall
---------
First uninstall the collective.plonetruegallery product just like you would
any other product. Then, go to ``portal_setup`` in the zmi and click on
the ``Import`` tab. Once there, select the 
``collective.plonetruegallery Uninstall Profile`` profile and run all the
steps. Once that is done, you can remove the egg from your buildout.


Fetching of Images Explained
----------------------------
* When rendering a picasa or flickr gallery, it checks if the images have been
  fetched within a day. If they have not, then it re-fetches the images for
  the gallery.
* You can also force a specific gallery to be re-fetched by appending
  ``@@refresh`` to the gallery url
* You can manually refresh all galleries on the site by typing in a url like
  ``mysite.com/@@refresh_all_galleries``  This means you can also setup a
  cron-like job to refresh all the galleries whenever you want to, just
  so it isn't done while a user is trying to render a page.


License Notes
-------------
This Plone product is under the GPL license; however, the Highslide JS display
type uses the `Creative Commons Attribution-NonCommercial 2.5 License
<http://creativecommons.org/licenses/by-nc/2.5/>`_ and is only for
non-commercial use unless you have purchased a commercial license from
the `Highslide <http://www.highslide.com/>`_ website.
collective.ptg.pixelentity gallery (under construction) also requires a license

Credits
=======

Coding Contributions
--------------------
* Patrick Gerken - huge help with 0.8 release
* Espen Moe-Nilssen
* Harald Friessnegger
* Sylvain Bouchard

Translations
------------
* French - Sylvain Boureliou
* Norwegian - Espen Moe-Nilssen
* Brazilian Portuguese - Diego Rubert
* Finnish - Ilja Everila
* German - Jens W. Klein, Harald Friessnegger
* Italian - Mirto Silvio Busico
* Spanish - Enrique Perez Arnaud
* Dutch - Rob Gietema, Martijn Schenk, Fred van Dijk

SDG

