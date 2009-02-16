from rdflib import Variable, Namespace
from telescope.sparql.query import SPARQLQuery
from telescope.sparql.helpers import *
from telescope.sparql.util import to_variable, to_list

__all__ = ['Select']

class Select(SPARQLQuery):
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
    query_form = 'SELECT'

    def __init__(self, variables, graph_pattern=None, **kwargs):
        self.variables = tuple(map(to_variable, variables))
        self._distinct = kwargs.pop('distinct', False)
        self._reduced = kwargs.pop('reduced', False)
        if self._distinct and self._reduced:
            raise ValueError("DISTINCT and REDUCED are mutually exclusive.")

        SPARQLQuery.__init__(self, graph_pattern, **kwargs)
    
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
    
