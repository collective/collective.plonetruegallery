collective.plonetruegallery Documentation
=========================================

Introduction
------------
collective.plonetruegallery is a Plone product that implements a very
customizable and sophisticated gallery. It allows you to add regular
Plone Galleries, Picasa Web Albums or even Flickr sets.  It also allows
the user to display the gallery in different sizes, choose between many
different javascript gallery display types and customize transitions, effects,
and timing.  This project aims to be everything you need for a Gallery in
Plone.

How It Works
------------
All you need to do is select the ``Gallery View`` from the ``Display`` drop down
item for any Folder or Collection content type. Once that is done, a
``Gallery Settings`` tab is enabled for the type. With this, you can customize
the various settings for the Gallery.


Supported Display Types
-----------------------

To install any of the various extra display types, you need to install
the dependant js package in buildout

 - galleria(ships with)
 - galleriffic(collective.js.galleriffic)
 - highslide(collective.js.highslide)
 - fancybox(collective.js.fancybox)
 - pikachoose(collective.js.s3slider)
 - s3slider(collective.js.pikachoose)
 - nivo slider(collective.js.nivoslider)
 - nivo gallery(collective.js.nivogallery)


Buildout configuration
~~~~~~~~~~~~~~~~~~~~~~

  eggs = 
    ...
    collective.plonetruegallery
    collective.js.highslide
    collective.js.fancybox
    collective.js.galleriffic
    collective.js.s3slider
    collective.js.pikachoose
    collective.js.nivoslider
    collective.js.nivogallery
    ...

Features
--------
* Flickr and Picasa Support!
* Customize gallery size, transition(limited transitions right now), timed and
  other settings
* Can use nested galleries
* searching and category selection for nested galleries
* Galleria, Galleriffic, Highslide JS, s3slider, Pikachoose and Fancybox display types
* display gallery inline
* Products.Collage integration


Flickr and Picasa Web Album Support
-----------------------------------
* to add support for these type of galleries you must install additional
  packages
* install flickrapi version 1.2 or higher for flickr support
* install gdata version 1.2.3 or higher for Picasa Web Album
  Support(tested with 1.3.3 and 2.0.12)
* on Plone 3.x you must also manually install hashlib for picasa support
* these can just be added to your buildout or installed with easy_install
  or you can add the package to your egg section like::

    collective.plonetruegallery[picasa] # for picasa support
    collective.plonetruegallery[flickr] # for flickr support
    collective.plonetruegallery[all] # for both flickr and picasa support


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

You will have to "whitelist" <object> and <param> in portal_transform safe-html.

Or you can do the same with an iframe


Troubleshouting safe-html
-------------------------

  If you have trouble, do this:
  Go to safe_html in portal_transforms tool
  Make sure param and object are valid tags (not nasty tag).

  After that, you should flush the cache of ZODB by going to
  1. Zope root app ZMI
  2. Control Panel
  3. Database
  4. main (or wathever zodb you have)
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
This Plone product is under the GLP license; however, the Highslide JS display
type uses the `Creative Commons Attribution-NonCommercial 2.5 License
<http://creativecommons.org/licenses/by-nc/2.5/>`_ and is only for
non-commercial use unless you have purchased a commercial license from
the `Highslide <http://www.highslide.com/>`_ website.

Credits
=======

Coding Contributions
--------------------
* Patrick Gerken - huge help with 0.8 release
* Espen Moe-Nilssen
* Harald Friessnegger

Translations
------------
* French - Sylvain Boureliou
* Norwegian - Espen Moe-Nilssen
* Brazilian Portuguese - Diego Rubert
* Finnish - Ilja Everila
* German - Jens W. Klein, Harald Friessnegger
* Italian - Mirto Silvio Busico
* Spanish - Enrique Perez Arnaud

SDG

