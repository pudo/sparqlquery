try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='telescope',
    version='0.1',
    keywords='rdf rdflib sparql orm',
    license='MIT',
    author="Brian Beck",
    description="RDF data mapper and SPARQL query builder",
    url='http://code.google.com/p/telescope/',
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    install_requires=['rdflib<3a'],
    test_suite='nose.collector',
    tests_require=['nose']
)
