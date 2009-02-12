from telescope.sparql.expressions import and_

__all__ = ['Triple', 'Filter', 'GraphPattern', 'GroupGraphPattern',
           'UnionGraphPattern', 'union', 'optional']

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

class Filter(object):
    def __init__(self, constraint):
        self.constraint = constraint
    
    def __repr__(self):
        return "Filter(%r)" % (self.constraint,)

class GraphPattern(object):
    def __init__(self, patterns):
        self.patterns = []
        self.filters = []
        self.add(*patterns)
    
    def add(self, *patterns):
        for pattern in patterns:
            if not isinstance(pattern, (Triple, GraphPattern)):
                pattern = Triple.from_obj(pattern)
            self.patterns.append(pattern)
    
    def filter(self, *expressions):
        self.filters.append(Filter(and_(*expressions)))
    
    def __nonzero__(self):
        return bool(self.patterns)
    
    def __len__(self):
        return len(self.patterns)
    
    def __getitem__(self, item):
        return self.patterns[item]
    
    def __or__(self, other):
        return UnionGraphPattern([self, GraphPattern.from_obj(other)])
    
    def __ror__(self, other):
        return UnionGraphPattern([GraphPattern.from_obj(other), self])
    
    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.patterns = self.patterns[:]
        clone.__dict__.update(kwargs)
        return clone
    
    @classmethod
    def from_obj(cls, obj, **kwargs):
        if isinstance(obj, GraphPattern):
            return obj._clone(**kwargs)
        else:
            if isinstance(obj, (Triple, GraphPattern)):
                obj = [obj]
            return cls(obj, **kwargs)

class GroupGraphPattern(GraphPattern):
    def __init__(self, patterns, optional=False):
        GraphPattern.__init__(self, patterns)
        self.optional = optional

class UnionGraphPattern(GraphPattern):
    def __init__(self, patterns):
        GraphPattern.__init__(self, patterns)

# Helpers. Users should import these from telescope.sparql.helpers.

def union(*patterns):
    from telescope.sparql.patterns import UnionGraphPattern, GraphPattern
    return UnionGraphPattern(map(GraphPattern.from_obj, patterns))

def optional(*patterns):
    from telescope.sparql.patterns import GroupGraphPattern
    return GroupGraphPattern(patterns, optional=True)

