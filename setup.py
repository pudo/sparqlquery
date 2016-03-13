from setuptools import setup, find_packages

setup(
    name='sparqlquery',
    version='0.2.2',
    keywords='rdf rdflib sparql orm',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    author='Brian Beck, Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    description='SPARQL query builder, fork of sparqlquery',
    url='https://github.com/pudo/sparqlquery',
    packages=find_packages(),
    install_requires=[
        'rdflib>=4.2.1'
    ],
    test_suite='nose.collector',
    tests_require=['nose']
)
