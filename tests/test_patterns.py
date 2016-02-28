from nose.tools import assert_raises
from sparqlquery import Variable, Namespace, URIRef
from sparqlquery.sparql.patterns import *
from sparqlquery.sparql.helpers import *

FOAF = Namespace('http://xmlns.com/foaf/0.1/')

class TestCreatingTriple:
    def test_args_set_subject_predicate_object(self):
        triple = Triple(Variable('x'), FOAF.name, "Alice")
        assert triple.subject == Variable('x')
        assert triple.predicate == FOAF.name
        assert triple.object == "Alice"
    
    def test_from_obj_with_triple_returns_same_object(self):
        triple_a = Triple(Variable('x'), FOAF.name, "Alice")
        triple_b = Triple.from_obj(triple_a)
        assert triple_a is triple_b
    
    def test_from_obj_with_sequence_unpacks_object_as_args(self):
        args = (Variable('x'), FOAF.name, "Alice")
        triple = Triple.from_obj(args)
        assert triple.subject == Variable('x')
        assert triple.predicate == FOAF.name
        assert triple.object == "Alice"
        assert_raises(TypeError, Triple.from_obj, 1)

    def test_from_obj_with_collection_pattern(self):
        args = (Variable('x'), FOAF.name, ("Alice", Variable('restaurant')))
        triple = Triple.from_obj(args)
        assert triple.subject == Variable('x')
        assert triple.predicate == FOAF.name
        assert triple.object == ("Alice", Variable('restaurant'))
        assert isinstance(triple.object, CollectionPattern)

    def test_nested_collection_patterns(self):
        args = (Variable('x'), FOAF.name, ("Alice", (Variable('y'), Variable('z'))))
        triple = Triple.from_obj(args)
        assert isinstance(triple.object, CollectionPattern)
        assert triple.object[0] == "Alice"
        assert isinstance(triple.object[1], CollectionPattern)
        assert triple.object[1][0] == Variable('y')
        assert triple.object[1][1] == Variable('z')

class TestIteratingTriple:
    def setup(self):
        self.triple = Triple(Variable('x'), FOAF.name, "Alice")
    
    def test_iteration_yields_subject_predicate_object(self):
        items = list(self.triple)
        assert len(items) == 3
        assert items[0] == Variable('x')
        assert items[1] == FOAF.name
        assert items[2] == "Alice"
    
    def test_iteration_does_not_consume_or_change_items(self):
        items_a = list(self.triple)
        items_b = list(self.triple)
        assert items_a == items_b

class TestPrintingTriple:
    def test_repr_args_print_with_repr(self):
        args = (Variable('x'), FOAF.name, "Alice")
        triple = Triple(*args)
        assert repr(triple) == "Triple(%r, %r, %r)" % args

class TestCreatingTriplesSameSubject:
    def test_first_arg_sets_subject(self):
        triples = TriplesSameSubject(v.x)
        assert triples.subject == v.x

class TestAddingPredicateObjectList:
    def test_second_arg_sets_predicate_object_list(self):
        triples = TriplesSameSubject(v.x, [(FOAF.name, v.name)])
        assert (FOAF.name, v.name) in triples.predicate_object_list
    
    def test_getitem_accepts_any_sequence_of_pairs(self):
        triples = TriplesSameSubject(v.x)
        for i in range(10):
            pairs = [(FOAF.name, j) for j in range(i)]
            new_triples = triples[pairs]
        for i in range(10):
            pairs = tuple([(FOAF.name, j) for j in range(i)])
            new_triples = triples[pairs]
        for i in range(10):
            pairs = ((FOAF.name, j) for j in range(i))
            new_triples = triples[pairs]
    
    def test_getitem_adds_predicate_object_pairs(self):
        triples = TriplesSameSubject(v.x)[(FOAF.name, v.name)]
        assert (FOAF.name, v.name) in triples.predicate_object_list
        new_triples = triples[(FOAF.knows, v.y)]
        assert (FOAF.knows, v.y) in new_triples.predicate_object_list
    
    def test_getitem_is_generative(self):
        triples = TriplesSameSubject(v.x)
        new_triples = triples[(FOAF.name, v.name)]
        assert new_triples is not triples
