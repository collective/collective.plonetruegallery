from lxml.html import fromstring
from zope.app.component.hooks import setSite
import transaction
from datetime import datetime, timedelta
import requests
import random
from plone.i18n.normalizer import idnormalizer
from StringIO import StringIO

SITE_ID = 'ptg'
START_FOLDER_ID = 'gallery'
NUM_GALLERIES = 20
START_DATE = datetime(2012, 1, 1)
MAX_GALLERY_SIZE = 100


def importit(app):

    site = app[SITE_ID]
    setSite(site)
    if START_FOLDER_ID not in site:
        site.invokeFactory('Folder', START_FOLDER_ID, title="Gallery")
        gallery = site[START_FOLDER_ID]
        gallery.setLayout('galleryview')
        gallery.reindexObject()
    else:
        gallery = site[START_FOLDER_ID]

    def populate(context, date):
        size = random.randint(20, MAX_GALLERY_SIZE)
        page = 1
        while len(context.objectIds()) < size:
            url = 'http://www.flickr.com/explore/interesting/%s/page%i/' % (
                date.strftime('%Y/%m/%d'), page)
            resp = requests.get(url)
            dom = fromstring(resp.content)
            for img in dom.cssselect('span.photo_container a img'):
                title = img.attrib['alt']
                id = idnormalizer.normalize(title).strip('_')
                if not id or id in context.objectIds():
                    continue
                print 'import %s' % title
                src = img.attrib['src'].replace('_m.', '_z.')
                imgresp = requests.get(src)
                context.invokeFactory('Image', id, title=title)
                imObj = context[id]
                imObj.setImage(StringIO(imgresp.content),
                               content_type="image/jpeg")
                imObj.reindexObject()
            page += 1

    date = START_DATE
    for num in range(NUM_GALLERIES):
        id = START_FOLDER_ID + '-' + str(num)
        print 'folder %s' % id
        if id not in gallery.objectIds():
            gallery.invokeFactory('Folder', id,
                                  title='Gallery ' + str(num + 1))
            folder = gallery[id]
            folder.setLayout('galleryview')
            folder.reindexObject()
        else:
            folder = gallery[id]
        date = date + timedelta(days=1)
        populate(folder, date)
        transaction.commit()
