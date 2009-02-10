from rdflib import ConjunctiveGraph, Variable, Namespace, URIRef, Literal
from telescope.sparql.expressions import Expression, and_, or_
from telescope.sparql.operators import op, fn, asc, desc
from telescope.sparql.select import Select, union, pattern, v
