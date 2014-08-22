from setuptools import setup, find_packages

setup(
    name='telescope',
    version='0.1',
    keywords='rdf rdflib sparql orm',
    license='MIT',
    author="Brian Beck",
    description="RDF data mapper and SPARQL query builder",
    url='http://code.google.com/p/telescope/',
    packages=find_packages(),
    #package_dir={'': 'lib'},
    install_requires=[
        'rdflib>=4.0.0'
    ],
    test_suite='nose.collector',
    tests_require=['nose']
)
