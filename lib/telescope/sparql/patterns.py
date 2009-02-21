import warnings
from telescope.sparql.expressions import and_

__all__ = ['Triple', 'TriplesSameSubject', 'Filter', 'GraphPattern',
           'GroupGraphPattern', 'UnionGraphPattern', 'union', 'optional']

class Triple(object):
    def __init__(self, subject, predicate, object):
        self.subject = subject
        self.predicate = predicate
        self.object = object
    
    def __iter__(self):
        return iter((self.subject, self.predicate, self.object))
    
    def __repr__(self):
        return "Triple(%r, %r, %r)" % tuple(self)
    
    @classmethod
    def from_obj(cls, obj):
        if isinstance(obj, Triple):
            return obj
        else:
            return cls(*obj)

class TriplesBlock(object):
    pass

class TriplesSameSubject(TriplesBlock):
    def __init__(self, subject, predicate_object_list=()):
        self.subject = subject
        self.predicate_object_list = tuple(predicate_object_list)
    
    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.__dict__.update(kwargs)
        return clone
    
    def _to_predicate_object_tuple(self, obj):
        if isinstance(obj, slice):
            if obj.step is not None:
                warnings.warn("Step value ignored: %r" % (obj.step,))
            return (obj.start, obj.stop)
        elif isinstance(obj, tuple) and len(obj) == 2:
            try:
                self._to_predicate_object_tuple(obj[0])
            except ValueError:
                return tuple(obj)
        raise ValueError("Could not convert to predicate-object pair: "
                         "%r is not a slice or valid 2-tuple" % (obj,))
    
    def __getitem__(self, predicate_object_pairs):
        predicate_object_list = list(self.predicate_object_list)
        try:
            pair = self._to_predicate_object_tuple(predicate_object_pairs)
        except ValueError:
            pairs = map(self._to_predicate_object_tuple, predicate_object_pairs)
            predicate_object_list.extend(pairs)
        else:
                predicate_object_list.append(pair)
        return self._clone(predicate_object_list=tuple(predicate_object_list))

class Filter(object):
    def __init__(self, constraint):
        self.constraint = constraint
    
    def __repr__(self):
        return "Filter(%r)" % (self.constraint,)

class GraphPattern(object):
    def __init__(self, patterns):
        self.patterns = []
        self.filters = []
        self.pattern(*patterns)
    
    def pattern(self, *patterns):
        for pattern in patterns:
            if not isinstance(pattern, (Triple, TriplesBlock, GraphPattern)):
                pattern = Triple.from_obj(pattern)
            self.patterns.append(pattern)
    
    def filter(self, *constraints):
        constraints = list(constraints)
        for i, constraint in enumerate(constraints):
            if isinstance(constraint, Filter):
                constraints[i] = constraint.constraint
        self.filters.append(Filter(and_(*constraints)))
    
    def __nonzero__(self):
        return bool(self.patterns or self.filters)
    
    def __or__(self, other):
        return UnionGraphPattern([self, GraphPattern.from_obj(other)])
    
    def __ror__(self, other):
        return UnionGraphPattern([GraphPattern.from_obj(other), self])
    
    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.patterns = self.patterns[:]
        clone.filters = self.filters[:]
        clone.__dict__.update(kwargs)
        return clone
    
    @classmethod
    def from_obj(cls, obj, **kwargs):
        if isinstance(obj, GraphPattern):
            return obj._clone(**kwargs)
        else:
            if isinstance(obj, (Triple, TriplesBlock, GraphPattern)):
                obj = [obj]
            return cls(obj, **kwargs)

class GroupGraphPattern(GraphPattern):
    def __init__(self, patterns, optional=False):
        super(GroupGraphPattern, self).__init__(patterns)
        self.optional = optional

class UnionGraphPattern(GraphPattern):
    def __init__(self, patterns):
        super(UnionGraphPattern, self).__init__(patterns)

# Helpers. Normally imported from telescope.sparql.helpers.

def union(*patterns):
    from telescope.sparql.patterns import UnionGraphPattern, GraphPattern
    return UnionGraphPattern(map(GraphPattern.from_obj, patterns))

def optional(*patterns):
    from telescope.sparql.patterns import GroupGraphPattern
    return GroupGraphPattern(patterns, optional=True)

