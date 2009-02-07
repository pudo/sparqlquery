#!/usr/bin/env python
import unittest
from rdflib import Namespace, ConjunctiveGraph, Variable, BNode, URIRef
from telescope.mapper import Mapper, mapper, query
from telescope.properties import Property, Relationship
import util

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')

class TestMapper(unittest.TestCase):
    def setUp(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person)
        self.graph = util.graph('foaf-01.rdf')
    
    def test_mapper_helper_returns_mapper(self):
        self.assert_(isinstance(self.mapper, Mapper))
    
    def test_default_identifier_is_class_name(self):
        self.assertEqual(self.mapper.identifier, Variable('Person'))

class TestQuery(unittest.TestCase):
    def setUp(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person)
        self.graph = util.graph('foaf-01.rdf')
    
    def test_query_returns_person_instance(self):
        persons = list(query(self.Person, self.graph))
        self.assertEqual(len(persons), 1)
        person = persons[0]
        self.assert_(type(person) is self.Person)

class TestMappedProperties(unittest.TestCase):
    def setUp(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person, properties={
            'name': Property(FOAF.name),
            'mbox': Property(FOAF.mbox)
        })
        self.graph = util.graph('foaf-01.rdf')
    
    def test_class_has_property_attrs(self):
        self.assert_(hasattr(self.Person, 'name'))
        self.assert_(hasattr(self.Person, 'mbox'))
    
    def test_instance_has_id(self):
        person = list(query(self.Person, self.graph))[0]
    
    def test_instance_id_is_bnode(self):
        person = list(query(self.Person, self.graph))[0]
        self.assert_(isinstance(person._id, BNode))
    
    def test_instance_has_bound_property_data(self):
        person = list(query(self.Person, self.graph))[0]
        self.assertEqual(person.name, "Peter Parker")
        self.assertEqual(person.mbox, URIRef("mailto:peter.parker@dailybugle.com"))

class TestMappedRelationships(unittest.TestCase):
    def setUp(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person, properties={
            'knows': Relationship(Person, FOAF.knows)
        })

if __name__ == '__main__':
    unittest.main()
