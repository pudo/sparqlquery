import operator
from rdflib import Literal

def n3(term):
    if hasattr(term, 'n3'):
        return term.n3()
    else:
        return Literal(term).n3()

class CompiledSelect(object):
    def __init__(self, select):
        self.select = select
        self._string = None
    
    def __unicode__(self):
        if self._string is None:
            self.compile()
        return self._string
    
    def compile(self):
        pass
    
    def execute(self, graph):
        return graph.query(unicode(self))