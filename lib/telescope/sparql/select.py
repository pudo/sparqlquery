from telescope.sparql.expressions import Expression, BinaryExpression
from telescope.sparql import operators

__all__ = ['Triple', 'Filter', 'GraphPattern', 'GroupGraphPattern', 'pattern', 'Select']

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
            if not isinstance(pattern, GraphPattern):
                pattern = Triple.from_obj(pattern)
            self.patterns.append(pattern)

    def filter(self, *filters):
        for filter in filters:
            if not isinstance(filter, Filter):
                filter = Filter(filter)
            self.filters.append(filter)
    
    def __nonzero__(self):
        return bool(self.patterns)

    def __len__(self):
        return len(self.patterns)
    
    def __getitem__(self, item):
        return self.patterns[item]

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
            if isinstance(obj, Triple):
                obj = [obj]
            return cls(obj, **kwargs)

class GroupGraphPattern(GraphPattern):
    def __init__(self, patterns, optional=False):
        GraphPattern.__init__(self, patterns)
        self.optional = optional

def pattern(*patterns, **kwargs):
    return GroupGraphPattern(patterns, **kwargs)

class Select(object):
    def __init__(self, variables, *patterns, **kwargs):
        self.variables = tuple(variables)
        self._where = GroupGraphPattern(patterns)
        self._distinct = kwargs.pop('distinct', False)
        self._reduced = kwargs.pop('reduced', False)
        if self._distinct and self._reduced:
            raise ValueError("DISTINCT and REDUCED are mutually exclusive.")
        
        self._limit = kwargs.pop('limit', None)
        self._offset = kwargs.pop('offset', None)
        self._order_by = kwargs.pop('order_by', None)
        self.graph = kwargs.pop('graph', None)
        if kwargs:
            key, value = kwargs.popitem()
            raise TypeError("Unexpected keyword argument: %r" % key)
    
    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.step is None or item.step == 1:
                offset = item.start
                limit = item.stop
                if offset is not None and limit is not None:
                    limit -= offset
                return self._clone(_offset=offset, _limit=limit)
            else:
                raise ValueError("Stepped slicing is not supported.")
        else:
            raise ValueError("Indexing is not supported.")
    
    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone._where = self._where._clone()
        clone.__dict__.update(kwargs)
        return clone
    
    def select(self, *variables):
        return self._clone(variables=self.variables + variables)
    
    def where(self, *patterns, **kwargs):
        clone = self._clone()
        if patterns:
            graph_pattern = GroupGraphPattern.from_obj(patterns, **kwargs)
            clone._where.add(graph_pattern)
        return clone
    
    def filter(self, *constraints, **kwargs):
        constraints = list(constraints)
        for key, value in kwargs.iteritems():
            expr = BinaryExpression(operators.eq, Variable(key), value)
            constraints.append(expr)
        clone = self._clone()
        clone._where.filter(*constraints)
        return clone
    
    def limit(self, number):
        """Return a new `Select` with LIMIT `number` applied."""
        return self._clone(_limit=number)
    
    def offset(self, number):
        """Return a new `Select` with OFFSET `number` applied."""
        return self._clone(_offset=number)
    
    def order_by(self, *variables):
        """Return a new `Select` with ORDER BY `variables` applied."""
        return self._clone(_order_by=variables)
    
    def distinct(self, value=True):
        """Return a new `Select` with DISTINCT modified according to `value`.
        
        If `value` is True (the default), then `reduced` is forced to False.
        """
        return self._clone(_distinct=value, _reduced=not value and self._reduced)
    
    def reduced(self, value=True):
        """Return a new `Select` with REDUCED modified according to `value`.
        
        If `value` is True (the default), then `distinct` is forced to False.
        """
        return self._clone(_reduced=value, _distinct=not value and self._distinct)
    
    def execute(self, graph):
        return graph.query(unicode(self.compile()))
    
    def compile(self, prefix_map=None):
        from telescope.sparql.compiler import SelectCompiler
        return SelectCompiler(self, prefix_map)

