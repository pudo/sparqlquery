from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='telescope',
    version='0.1',
    description="Observe SPARQLing RDF constellations through Python objects.",
    url='http://code.google.com/p/telescope/',
    packages=find_packages(),
    install_requires=['rdflib<3a'],
    test_suite='nose.collector'
)
