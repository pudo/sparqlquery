from rdflib import Literal

def n3(term):
    if hasattr(term, 'n3'):
        return term.n3()
    else:
        return Literal(term).n3()

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
    
    def compile(self):
        return ' '.join(map(n3, self))

class GraphPattern(object):
    def __init__(self, *triples):
        self.triples = map(Triple.from_obj, triples)
    
    @classmethod
    def from_obj(cls, obj):
        if isinstance(obj, GraphPattern):
            return obj
        else:
            return cls(*obj)
    
    def compile(self):
        return '{\n%s\n}' % ' .\n'.join(t.compile() for t in self.triples)

class Select(object):
    def __init__(self, variables, *graph_patterns):
        self.variables = list(variables)
        self.graph_patterns = map(GraphPattern.from_obj, graph_patterns)
    
    def execute(self, graph):
        return graph.query(self.compile())
    
    def compile(self):
        variables = ' '.join(map(n3, self.variables))
        if len(self.graph_patterns) == 1:
            patterns = self.graph_patterns[0].compile()
        else:
            compiled = [pattern.compile() for pattern in self.graph_patterns]
            patterns = '{\n%s\n}' % '\n'.join(compiled)
        return 'SELECT %s\nWHERE %s' % (variables, patterns)
