from rdflib import Namespace, Variable, Literal, URIRef
from telescope.sparql.select import Triple

__all__ = ['Term', 'Property', 'Label', 'Collection', 'Single']

RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')

class Term(object):
    def __init__(self, predicate, default=None):
        self.predicate = predicate
        self.default = default
    
    def __get__(self, instance, owner):
        if instance is not None:
            try:
                instance._state
            except AttributeError:
                return self.default
            else:
                return instance._state.get(self, self.default)
        return self
    
    def __set__(self, instance, value):
        try:
            instance._state
        except AttributeError:
            instance._state = {}
        instance._state[self] = value
    
    def to_python(self, graph, value):
        return value
    
    def resolve_subject(self, graph, uri):
        return uri
    
    def build_triples(self, subject, object):
        yield Triple(subject, self.predicate, object)

class Property(Term):
    def to_python(self, graph, value):
        if isinstance(value, Literal):
            value = value.toPython()
            if isinstance(value, Literal):
                return unicode(value)
            else:
                return value
        elif isinstance(value, URIRef):
            return self.resolve_subject(graph, value)
        else:
            return value

class Label(Property):
    def resolve_subject(self, graph, uri):
        for label in graph.objects(uri, RDFS.label):
            return self.to_python(graph, label)
        return uri

class Collection(object):
    def __init__(self, class_):
        self.class_ = class_

class Single(Collection):
    pass

class PropertyManager(object):
    def __init__(self, class_):
        self.class_ = class_
        self.names = {}
        self.properties = {}
    
    def __getitem__(self, key):
        return self.properties[key]
    
    def __setitem__(self, key, value):
        return self.add_property(key, value)
    
    def __iter__(self):
        return self.properties.iteritems()
    
    def get(self, key, default=None):
        return self.properties.get(key, default)
    
    def add_property(self, key, descriptor):
        self.names[descriptor] = key
        self.properties[key] = descriptor
        setattr(self.class_, key, descriptor)
    
    def update(self, properties):
        if isinstance(properties, PropertyManager):
            properties = properties.properties
        for key, descriptor in properties.iteritems():
            self.add_property(key, descriptor)

