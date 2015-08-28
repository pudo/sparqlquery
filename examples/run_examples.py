#!/bin/bash -ex
cd "$( dirname "${BASH_SOURCE[0]}" )"
rapper -i turtle data.turtle -o rdfxml > data.rdf
RDF_DIRECTORY="." PYTHONPATH=".." python ptrec.py data 1999-03-01 2
