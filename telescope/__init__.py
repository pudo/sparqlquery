import rdflib
try:
    from rdflib import ConjunctiveGraph, Namespace, Variable, URIRef, Literal, BNode
except ImportError:
    from rdflib.graph import ConjunctiveGraph
    from rdflib.term import Namespace, Variable, URIRef, Literal, BNode
from telescope.sparql.expressions import Expression
from telescope.sparql.queryforms import *
from telescope.sparql.helpers import *
