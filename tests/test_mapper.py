from nose.tools import assert_raises
from sparqlquery import Namespace, ConjunctiveGraph, Variable, BNode, URIRef
from sparqlquery.mapper import Mapper, mapper
from sparqlquery.mapper.properties import Property, Relationship
from sparqlquery.mapper.query import Query
from sparqlquery.mapper.session import Session
import helpers

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')

class TestMapper:
    def setup(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person)
        self.session = Session(helpers.graph('foaf-01.rdf'))
    
    def test_mapper_helper_returns_mapper(self):
        assert isinstance(self.mapper, Mapper)
    
    def test_default_identifier_is_class_name(self):
        assert self.mapper.identifier == Variable('Person')

class TestQuery:
    def setup(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person)
        self.session = Session(helpers.graph('foaf-01.rdf'))
    
    def test_session_query_returns_query_instance(self):
        query = self.session.query(self.Person)
        assert isinstance(query, Query)
    
    def test_query_returns_person_instance(self):
        persons = list(self.session.query(self.Person))
        assert len(persons) == 1
        person = persons[0]
        assert type(person) is self.Person

class TestMappedProperties:
    def setup(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person, properties={
            'name': Property(FOAF.name),
            'mbox': Property(FOAF.mbox)
        })
        self.session = Session(helpers.graph('foaf-01.rdf'))
    
    def test_class_has_property_attrs(self):
        assert hasattr(self.Person, 'name')
        assert hasattr(self.Person, 'mbox')
    
    def test_instance_has_id(self):
        person = list(self.session.query(self.Person))[0]
        assert getattr(person, '_id', None) is not None
    
    def test_instance_id_is_bnode(self):
        person = list(self.session.query(self.Person))[0]
        assert isinstance(person._id, BNode)
    
    def test_instance_has_bound_property_data(self):
        person = list(self.session.query(self.Person))[0]
        assert person.name == "Peter Parker"
        assert person.mbox == URIRef("mailto:peter.parker@dailybugle.com")

class TestMappedRelationships:
    def setup(self):
        class Person(object):
            pass
        self.Person = Person
        self.mapper = mapper(Person, FOAF.Person, properties={
            'knows': Relationship(Person, FOAF.knows)
        })
