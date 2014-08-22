from telescope.sparql.patterns import GroupGraphPattern
from telescope.sparql.util import to_variable, to_list

__all__ = ['SPARQLQuery', 'SolutionModifierSupportingQuery',
           'ProjectionSupportingQuery']

class SPARQLQuery(object):
    """Programmatically build a SPARQL query."""
    
    def __init__(self, pattern=None):
        if pattern is None:
            pattern = GroupGraphPattern([])
        elif not isinstance(pattern, GroupGraphPattern):
            pattern = GroupGraphPattern.from_obj(pattern)
        self._where = pattern
    
    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone._where = self._where._clone()
        clone.__dict__.update(kwargs)
        return clone
    
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
    
    def execute(self, graph, prefix_map=None):
        """Compile and execute this query on `graph`.
        
        If `prefix_map` is given, use it as a mapping from `rdflib.Namespace`
        instances to prefixed names to use in the compiled query.
        
        """
        return graph.query(unicode(self.compile(prefix_map)))
    
    def _get_compiler_class(self):
        from telescope.sparql.compiler import QueryCompiler
        return QueryCompiler

    def compile(self, prefix_map=None, compiler_class=None):
        """Compile this query and return the resulting string.
        
        If `prefix_map` is given, use it as a mapping from `rdflib.Namespace`
        instances to prefixed names to use in the compiled query.
        
        """
        compiler_class = self._get_compiler_class()
        compiler = compiler_class(prefix_map)
        return compiler.compile(self)


class SolutionModifierSupportingQuery(SPARQLQuery):
    """
    Programmatically build a SPARQL query that supports the solution modifiers
    ORDER_BY, LIMIT, and OFFSET.
    
    """
    
    def __init__(self, pattern=None, order_by=None, limit=None, offset=None):
        super(SolutionModifierSupportingQuery, self).__init__(pattern)
        self._order_by = order_by
        self._limit = limit
        self._offset = offset
    
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
    
    def _get_compiler_class(self):
        from telescope.sparql.compiler import SolutionModifierSupportingQueryCompiler
        return SolutionModifierSupportingQueryCompiler

    def order_by(self, *expressions):
        """Return a new `Select` with an ORDER BY clause.
        
        If no arguments are given, the query will not have an ORDER BY clause.
        
        """
        return self._clone(_order_by=expressions or None)
    
    def limit(self, limit):
        """Return a new `Select` with a LIMIT clause.
        
        If `limit` is None, the query will not have a LIMIT clause.
        
        """
        return self._clone(_limit=limit)
    
    def offset(self, offset):
        """Return a new `Select` with an OFFSET clause.
        
        If `offset` is None, the query will not have an OFFSET clause.
        
        """
        return self._clone(_offset=offset)


class ProjectionSupportingQuery(SolutionModifierSupportingQuery):
    """Programmatically build a SPARQL query that supports projection."""
    
    def __init__(self, projection, pattern=None, order_by=None, limit=None,
                 offset=None):
        super(ProjectionSupportingQuery, self).__init__(pattern,
                                                        order_by=order_by,
                                                        limit=limit,
                                                        offset=offset)
        if projection != '*':
            projection = map(to_variable, to_list(projection))
        self.projection = tuple(projection)
    
    def _get_compiler_class(self):
        from telescope.sparql.compiler import ProjectionSupportingQueryCompiler
        return ProjectionSupportingQueryCompiler

    def project(self, *terms, **kwargs):
        """
        Return a new `Select` with the given terms projected in the SELECT
        clause.
        
        Each argument may be a variable or a sequence of variables, and each
        variable is converted to a `rdflib.Variable` instance using
        `to_variable` (which means variables may also be specified as strings
        and `Expression` instances).
        
        If the keyword-only argument `append` is true, the specified variables
        will be appended to the current projection instead of replacing it.
        
        """
        append = kwargs.pop('append', False)
        projection = append and list(self.projection) or []
        for arg in terms:
            for variable in map(to_variable, to_list(arg)):
                projection.append(variable)
        return self._clone(projection=tuple(projection))

