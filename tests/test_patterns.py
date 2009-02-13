from nose.tools import assert_raises
from rdflib import Namespace, URIRef
from telescope.sparql.patterns import *
from telescope.sparql.helpers import *

FOAF = Namespace('http://xmlns.com/foaf/0.1/')

class TestCreatingTriplesSameSubject:
    def test_first_arg_sets_subject(self):
        triples = TriplesSameSubject(v.x)
        assert triples.subject == v.x

class TestAddingPredicateObjectList:
    def test_second_arg_sets_predicate_object_list(self):
        triples = TriplesSameSubject(v.x, [(FOAF.name, v.name)])
        assert (FOAF.name, v.name) in triples.predicate_object_list

    def test_getitem_adds_predicate_object_pairs(self):
        triples = TriplesSameSubject(v.x)[(FOAF.name, v.name)]
        assert (FOAF.name, v.name) in triples.predicate_object_list
        new_triples = triples[(FOAF.knows, v.y)]
        assert (FOAF.knows, v.y) in new_triples.predicate_object_list
    
    def test_getitem_is_generative(self):
        triples = TriplesSameSubject(v.x)
        new_triples = triples[(FOAF.name, v.name)]
        assert new_triples is not triples
