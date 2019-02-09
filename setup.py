# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

import os


version = '3.4.9.dev0'

setup(
    name='collective.plonetruegallery',
    version=version,
    description="A gallery/slideshow product for Plone that can aggregate "
    "from Picasa (add collective.ptg.flickr) and Flickr (add collective.ptg.flickr) or use Plone images.",
    long_description=open("README.rst").read()
    + "\n"
    + open(os.path.join("docs", "HISTORY.txt")).read(),
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
        'plone.api',
        'Products.CMFPlone>=5',
        'setuptools',
    ],
    extras_require={
        'test': ['plone.app.testing', 'plone.testing', 'unittest2'],
        'at': ['Products.Archetypes', 'Products.ATContentTypes'],
    },
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
)
