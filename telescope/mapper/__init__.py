from telescope import Variable
from telescope.exceptions import *
from telescope.sparql.patterns import Triple
from telescope.sparql.queryforms import Select
from telescope.sparql.helpers import is_a
from telescope.mapper.properties import PropertyManager
from telescope.mapper.query import Query

__all__ = ['Mapper', 'mapper', 'get_mapper']

class Mapper(object):
    def __init__(self, class_, type_or_select, identifier=None, properties=None):
        self.class_ = class_
        
        if identifier is None:
            identifier = Variable(class_.__name__)
        self.identifier = identifier
        
        if isinstance(type_or_select, Select):
            select = type_or_select
        else:
            rdf_type = type_or_select
            select = Select([identifier], [(identifier, is_a, rdf_type)])
        
        if identifier not in select.projection:
            raise InvalidRequestError("Select must include identifier.")
        
        self.select = select
        self.setup_class(properties or {})
    
    def setup_class(self, properties):
        if not hasattr(self.class_, '_manager'):
            self.class_._manager = PropertyManager(self.class_)
        self.class_._manager.update(properties)
    
    def new_instance(self):
        return self.class_.__new__(self.class_)
    
    def bind_instance(self, graph, instance, data):
        instance._id = data.pop(self.identifier)
        for key, value in data.iteritems():
            descriptor = self.class_._manager.get(key)
            if descriptor is not None:
                value = descriptor.to_python(graph, value)
                descriptor.__set__(instance, value)
    
    def bind_results(self, graph, query, results):
        for result in results:
            data = dict(zip(query.projection, result))
            instance = self.new_instance()
            self.bind_instance(graph, instance, data)
            yield instance

def mapper(class_, *args, **kwargs):
    class_._mapper = Mapper(class_, *args, **kwargs)
    return class_._mapper

def get_mapper(class_):
    return class_._mapper
