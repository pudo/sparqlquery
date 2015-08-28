#!/bin/bash -ex
cd "$( dirname "${BASH_SOURCE[0]}" )"
if [[ ! -e data.rdf ]]; then
    if hash rapper 2>/dev/null; then
        rapper -i turtle data.turtle -o rdfxml > data.rdf
    else
        >&2 echo "$0 needs the example dataset as RDF. I would use 'rapper', but it does not exist. On Ubuntu, install raptor2-utils. Exiting with error."
        exit 1
    fi
fi
RDF_DIRECTORY="." PYTHONPATH=".." ../pyenv/bin/python2 ptrec.py data 1999-03-01 2
