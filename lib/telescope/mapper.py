from rdflib import Namespace, Variable, Literal, URIRef
from telescope.properties import Term
from telescope.sparql.expressions import Select

__all__ = ['Mapper', 'mapper', 'query']

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

class Mapper(object):
    PROPERTIES = {'_id': Term(RDF.type)}
    
    def __init__(self, class_, rdf_type, properties=None):
        self.class_ = class_
        self.rdf_type = rdf_type
        self.setup_class(properties or {})
    
    def setup_class(self, properties):
        if not hasattr(self.class_, '_manager'):
            self.class_._manager = PropertyManager(self.class_)
        self.class_._manager.update(self.PROPERTIES)
        self.class_._manager.update(properties)
    
    def new_instance(self):
        return self.class_.__new__(self.class_)
    
    def setup_instance(self, instance):
        instance._state = {}
    
    def bind_instance(self, graph, instance, data):
        for key, value in data.iteritems():
            descriptor = self.class_._manager.get(key)
            if descriptor is not None:
                value = descriptor.to_python(graph, value)
                descriptor.__set__(instance, value)
    
    def map_results(self, graph, query, results):
        variables = query.variables
        for result in results:
            data = dict(zip(variables, result))
            instance = self.new_instance()
            yield instance
            self.bind_instance(graph, instance, data)
            yield instance
    
    def query(self, graph):
        terms = dict(self.class_._manager)
        variables = map(Variable, terms)
        term = terms.pop('_id')
        instance = Variable('_id')
        triples = list(term.build_triples(instance, self.rdf_type))
        for name, term in terms.iteritems():
            triples.extend(term.build_triples(instance, Variable(name)))
        select = Select(variables, triples)
        results = select.execute(graph)
        return self.map_results(graph, select, results)

def mapper(class_, rdf_type, properties=None):
    class_._mapper = Mapper(class_, rdf_type, properties)
    return class_._mapper

def query(class_, graph):
    return class_._mapper.query(graph)
