#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

long_description = open('README.rst', 'r').read()

with open('VERSION') as version_file:
    version = version_file.read()
    version = version.strip()

install_requirements = [
    'Flask>=0.10.1',
    'mongoengine>=0.10.0',
    'flask-mongoengine>=0.7.4',
    'Flask-Assets>=0.11',
    'jsmin>=2.1.6',
    'cssmin>=0.2.0',
    'webassets>=0.11.1',
    'Flask-Admin>=1.4.0',
    'Flask-SQLAlchemy>=2.1',
    'Flask-Security>=1.7.4',
    'Flask-Login>=0.3.2',
    'Flask-Script>=2.0.5',
    'Flask-Mail>=0.9.1',
    'Flask-BabelEx>=0.9.2',
    'Flask-Testing>=0.4.2',
    'Flask-Migrate>=1.7.0',
    'unicodecsv>=0.14.1',
    'opac_schema',
    # for production production
    'chaussette>=1.3',
    'gevent>=1.1.0',
]

dependency_links = [
    'http://github.com/scieloorg/opac_schema/tarball/v2.23#egg=opac_schema-v2.24'
]

setup(
    name='opac',
    version=version,
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requirements,
    dependency_links=dependency_links,
)
