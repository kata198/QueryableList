#!/usr/bin/env python
#
# Copyright (c) 2016, 2017 Timothy Savannah under terms of LGPLv2.
#  You should have received a copy of this with this distribution as "LICENSE"


#vim: set ts=4 st=4 sw=4 expandtab

import os
from setuptools import setup


if __name__ == '__main__':
 

    dirName = os.path.dirname(__file__)
    if dirName and os.getcwd() != dirName:
        os.chdir(dirName)

    summary = 'Python module to add support for ORM-style filtering to any list of items'

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Exception when reading long description: %s\n' %(str(e),))
        long_description = summary

    setup(name='QueryableList',
            version='3.1.0',
            packages=['QueryableList'],
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            url='https://github.com/kata198/QueryableList',
            maintainer_email='kata198@gmail.com',
            description=summary,
            long_description=long_description,
            license='LGPLv2',
            keywords=['queryablelist', 'query', 'list', 'filter', 'objects', 'eq', 'ne', 'lt', 'gt', 'equals', 'not', 'compare', 'comprehension', 'orm', 'queryable', 'django', 'flask', 'indexedredis', 'contains', 'icontains'],
            classifiers=['Development Status :: 5 - Production/Stable',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Programming Language :: Python :: 3.5',
                          'Programming Language :: Python :: 3.6',
                          'Topic :: Software Development :: Libraries :: Python Modules',
            ]
    )



#vim: set ts=4 st=4 sw=4 expandtab
