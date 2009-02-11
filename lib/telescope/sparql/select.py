from rdflib import Variable, Namespace
from telescope.sparql.expressions import Expression, and_
from telescope.sparql.patterns import GroupGraphPattern
from telescope.sparql.util import to_variable, to_list, v

__all__ = ['Select']

class Select(object):
    """
    Programmatically build SPARQL SELECT queries.
    
    Creating a `Select` requires at least a list of variables to project, which
    may be given as `Variable`, `Expression`, or string instances:
    
    >>> query = Select([Variable('x'), v.name, 'mbox'])
    >>> print query.compile()
    SELECT ?x ?name ?mbox
    WHERE { }
    
    Patterns and constraints are added with the `where` and `filter` methods,
    respectively:
    
    >>> FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    >>> query = query.where((v.x, FOAF.name, v.name)).filter(v.name == "Brian")
    >>> print query.compile({FOAF: 'foaf'})
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?x ?name ?mbox
    WHERE { ?x foaf:name ?name . FILTER (?name = "Brian") }

    """
    def __init__(self, variables, *patterns, **kwargs):
        self.variables = tuple(map(to_variable, variables))
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
    
    def project(self, *variables, **kwargs):
        add = kwargs.pop('add', False)
        projection = []
        for arg in variables:
            for variable in map(to_variable, to_list(arg)):
                if variable:
                    projection.append(variable)
        if add:
            projection[:0] = self.variables
        return self._clone(variables=tuple(projection))
    
    def where(self, *patterns, **kwargs):
        clone = self._clone()
        if patterns:
            graph_pattern = GroupGraphPattern.from_obj(patterns, **kwargs)
            clone._where.add(graph_pattern)
        return clone
    
    def filter(self, *constraints, **kwargs):
        constraints = list(constraints)
        for key, value in kwargs.iteritems():
            constraints.append(v[key] == value)
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
    
    def execute(self, graph, prefix_map=None):
        return graph.query(unicode(self.compile(prefix_map)))
    
    def compile(self, prefix_map=None):
        from telescope.sparql.compiler import SelectCompiler
        compiler = SelectCompiler(prefix_map)
        return compiler.compile(self)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

