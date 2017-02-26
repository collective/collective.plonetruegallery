# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

import os

version = '3.4.8'

setup(name='collective.plonetruegallery',
      version=version,
      description="A gallery/slideshow product for Plone that can aggregate "
                  "from Picasa (add collective.ptg.flickr) and Flickr (add collective.ptg.flickr) or use Plone images.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Plone :: 4.1',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          'Framework :: Plone :: 5.0',
          'Framework :: Plone',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='gallery plone slideshow photo photos image images picasa '
               'flickr highslide nivoslider nivogallery pikachoose fancybox supersized quicksand'
               'galleriffic galleria',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='https://github.com/collective/collective.plonetruegallery',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.ptg.galleria',
          'plone.app.collection',
          'plone.app.contentmenu',
          'plone.app.form',
          'plone.app.imaging',
          'plone.app.portlets',
          'plone.app.querystring',
          'plone.app.vocabularies',
          'plone.app.z3cform',
          'plone.api',
          'plone.folder',
          'plone.memoize',
          'plone.portlets',
          'plone.uuid',
          'plone.z3cform',
          'Products.Archetypes',
          'Products.ATContentTypes',
          'Products.CMFCore',
          'Products.CMFPlone >=4.1',
          'Products.GenericSetup',
          'setuptools',
          'transaction',
          'z3c.form',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.testing',
              'unittest2',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
)
