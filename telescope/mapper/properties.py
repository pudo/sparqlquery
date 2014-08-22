from telescope import Namespace, Variable, Literal, URIRef
from telescope.sparql.patterns import Triple

__all__ = ['Term', 'Property', 'Label']

RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')

class Term(object):
    def __init__(self, predicate, default=None):
        self.predicate = predicate
        self.default = default
    
    def __get__(self, instance, owner):
        if instance is not None:
            state = instance.__dict__.get('_state', {})
            return state.get(self, self.default)
        return self
    
    def __set__(self, instance, value):
        state = instance.__dict__.setdefault('_state', {})
        state[self] = value
    
    def to_python(self, graph, value):
        return value
    
    def resolve_subject(self, graph, uri):
        return uri
    
    def triples(self, subject, object):
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

class Relationship(Property):
    def __init__(self, class_, predicate):
        self.class_ = class_
        self.predicate = predicate
    
    def __get__(self, instance, owner):
        if instance is not None:
            state = instance.__dict__.get('_state', {})
            return state.get(self, [])
        return self
    
    def triples(self, subject, object):
        related_mapper = self.class_._mapper
        related_mapper.select._clone(variables=(related_mapper.identifier,))
        

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
    
    def update(self, properties, **kwargs):
        properties = dict(properties, **kwargs)
        for key, descriptor in properties.iteritems():
            self.add_property(key, descriptor)
