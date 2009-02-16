from rdflib import Variable, Namespace
from telescope.sparql.expressions import Expression
from telescope.sparql.patterns import GroupGraphPattern
from telescope.sparql.helpers import *
from telescope.sparql.util import to_variable, to_list

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
        """
        Return a new `Select` with the given variables projected in the SELECT
        clause.
        
        Each argument may be a variable or a sequence of variables, and each
        variable is converted to a `rdflib.Variable` instance using
        `to_variable` (which means variables may also be specified as strings
        and `Expression` instances).
        
        If the keyword-only argument `add` is true, the specified variables will
        be added to the projection instead of replacing the current projection.
        
        """
        add = kwargs.pop('add', False)
        projection = add and list(self.variables) or []
        for arg in variables:
            for variable in map(to_variable, to_list(arg)):
                projection.append(variable)
        return self._clone(variables=tuple(projection))
    
    def where(self, *patterns, **kwargs):
        """Return a new `Select` with the given patterns in the WHERE clause.
        
        Each argument may be a triple (a 3-tuple or `Triple` instances) or a
        `GraphPattern` instance.  The patterns are added to the WHERE clause in
        the order specified.
        
        If the keyword-only `optional` argument is true, add all given patterns
        to an OPTIONAL graph pattern.
        
        """
        clone = self._clone()
        if patterns:
            graph_pattern = GroupGraphPattern.from_obj(patterns, **kwargs)
            clone._where.pattern(graph_pattern)
        return clone
    
    def filter(self, *constraints, **kwargs):
        """Return a new `Select` with the given constraints in the WHERE clause.
        
        Each positional argument may be an `Expression`, `Filter`, or literal.
        Each keyword argument specifies a binary '=' expression, where the
        argument name is the variable name on the left and the value is the
        expression on the right.
        
        All constraints given in a single call to this method will be combined
        (with '&&') into a single conditional expression.
        
        """
        constraints = list(constraints)
        for key, value in kwargs.iteritems():
            constraints.append(v[key] == value)
        clone = self._clone()
        clone._where.filter(*constraints)
        return clone
    
    def limit(self, number):
        """Return a new `Select` with a LIMIT `number` clause.
        
        If `number` is None, the query will not have a LIMIT clause.
        
        """
        return self._clone(_limit=number)
    
    def offset(self, number):
        """Return a new `Select` with an OFFSET `number` clause.
        
        If `number` is None, the query will not have an OFFSET clause.
        
        """
        return self._clone(_offset=number)
    
    def order_by(self, *variables):
        """Return a new `Select` with an ORDER BY `variables` clause.
        
        If the singular argument None is given, the query will not have an
        ORDER BY clause.
        
        """
        return self._clone(_order_by=variables)
    
    def distinct(self, value=True):
        """
        Return a new `Select` with the DISTINCT modifier (or without it if
        `value` is false).
        
        If `value` is true (the default), then `reduced` is forced to False.
        
        """
        return self._clone(_distinct=value, _reduced=not value and self._reduced)
    
    def reduced(self, value=True):
        """Return a new `Select` with the REDUCED modifier (or without it if
        `value` is false).
        
        If `value` is true (the default), then `distinct` is forced to False.
        
        """
        return self._clone(_reduced=value, _distinct=not value and self._distinct)
    
    def execute(self, graph, prefix_map=None):
        """Compile and execute this query on `graph`.
        
        If `prefix_map` is given, use it as a mapping from `rdflib.Namespace`
        instances to prefixed names to use in the compiled query.
        
        """
        return graph.query(unicode(self.compile(prefix_map)))
    
    def compile(self, prefix_map=None):
        """Compile this query and return the resulting string.
        
        If `prefix_map` is given, use it as a mapping from `rdflib.Namespace`
        instances to prefixed names to use in the compiled query.
        
        """
        from telescope.sparql.compiler import SelectCompiler
        compiler = SelectCompiler(prefix_map)
        return compiler.compile(self)
