import operator
try:
    from rdflib import Namespace
except ImportError:
    from rdflib.term import Namespace
from sparqlquery.sparql.expressions import VariableExpressionConstructor, and_
from sparqlquery.sparql.expressions import or_
from sparqlquery.sparql.operators import Operator, BuiltinOperatorConstructor
from sparqlquery.sparql.operators import FunctionConstructor
from sparqlquery.sparql.patterns import union, optional, graph, filter
from sparqlquery.sparql.patterns import TriplesSameSubject as subject

__all__ = ['RDF', 'RDFS', 'OWL', 'XSD', 'FN', 'is_a', 'v', 'op', 'fn', 'asc',
           'desc', 'and_', 'or_', 'union', 'optional', 'graph', 'func',
           'filter']

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')
FN = Namespace('http://www.w3.org/2005/xpath-functions#')

is_a = RDF.type
v = VariableExpressionConstructor()
op = BuiltinOperatorConstructor()
fn = op(FN)
asc = Operator('ASC')
desc = Operator('DESC')
func = FunctionConstructor()
