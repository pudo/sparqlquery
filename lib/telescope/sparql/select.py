__all__ = ['Triple', 'GraphPattern', 'pattern', 'Select']

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

class GraphPattern(object):
    def __init__(self, patterns, optional=False):
        self.patterns = []
        for pattern in patterns:
            if not isinstance(pattern, GraphPattern):
                pattern = Triple.from_obj(pattern)
            self.patterns.append(pattern)
        self.optional = optional
    
    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.patterns = self.patterns[:]
        clone.optional = self.optional
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

def pattern(*patterns, **kwargs):
    return GraphPattern(patterns, **kwargs)

class Select(object):
    def __init__(self, variables, *patterns, **kwargs):
        self.variables = list(variables)
        if patterns:
            self.patterns = [GraphPattern.from_obj(patterns)]
        else:
            self.patterns = []
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
        clone.variables = self.variables[:]
        clone.patterns = self.patterns[:]
        clone.__dict__.update(kwargs)
        return clone
    
    def where(self, *patterns, **kwargs):
        clone = self._clone()
        if patterns:
            clone.patterns.append(GraphPattern.from_obj(patterns, **kwargs))
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

