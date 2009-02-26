from telescope.mapper import mapper
from telescope.mapper.properties import PropertyManager, Term

class DeclarativeMeta(type):
    def __init__(cls, name, bases, attrs):
        manager = cls._manager = PropertyManager(cls)
        for base in reversed(bases):
            if hasattr(base, '_manager'):
                manager.update(base._manager)
        for key, value in attrs.iteritems():
            if isinstance(value, Term):
                manager.add_property(key, value)
        if hasattr(cls, 'RDF_TYPE'):
            mapper(cls, cls.RDF_TYPE)

class Subject(object):
    __metaclass__ = DeclarativeMeta
    
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls, *args, **kwargs)
        cls._mapper.setup_instance(instance)
        return instance
