from telescope.exceptions import *
from telescope.sparql.query import *

__all__ = ['Ask', 'Construct', 'Select', 'Describe']

class Ask(SPARQLQuery):
    """Programmatically build a SPARQL ASK query."""


class Construct(SolutionModifierSupportingQuery):
    """Programmatically build a SPARQL CONSTRUCT query."""
    
    def __init__(self, template, pattern=None, order_by=None, limit=None,
                 offset=None):
        super(Construct, self).__init__(pattern, order_by, limit, offset)
        self._template = template
    
    def template(self, template):
        return self._clone(_template=template)


class Select(ProjectionSupportingQuery):
    """Programmatically build a SPARQL SELECT query."""
    
    def __init__(self, projection, pattern=None, distinct=False,
                 reduced=False, order_by=None, limit=None, offset=None):
        super(Select, self).__init__(projection, pattern, order_by=order_by,
                                     limit=limit, offset=offset)
        if distinct and reduced:
            raise InvalidRequestError("DISTINCT and REDUCED are mutually exclusive.")
        self._distinct = distinct
        self._reduced = reduced
    
    def distinct(self, flag=True):
        """
        Return a new `Select` with the DISTINCT modifier (or without it if
        `flag` is false).
        
        If `flag` is true (the default), then `reduced` is forced to False.
        
        """
        return self._clone(_distinct=flag, _reduced=not flag and self._reduced)
    
    def reduced(self, flag=True):
        """Return a new `Select` with the REDUCED modifier (or without it if
        `flag` is false).
        
        If `flag` is true (the default), then `distinct` is forced to False.
        
        """
        return self._clone(_reduced=flag, _distinct=not flag and self._distinct)


class Describe(ProjectionSupportingQuery):
    """Programmatically build a SPARQL DESCRIBE query."""
