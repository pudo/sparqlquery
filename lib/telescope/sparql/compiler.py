from rdflib import Literal, URIRef
from telescope.sparql import operators
from telescope.sparql.select import Select, Triple, GraphPattern, GroupGraphPattern

def n3(term):
    if hasattr(term, 'n3'):
        return term.n3()
    else:
        return Literal(term).n3()

def defrag(uri):
    if '#' in uri:
        namespace, fragment = uri.split('#', 1)
        return ('%s#' % namespace, fragment)
    return (uri, None)

class SelectCompiler(object):
    OPERATORS = {
        operators.and_: '&&',
        operators.or_: '||',
        operators.invert: '!',
        operators.pos: '+',
        operators.neg: '-',
        operators.eq: '=',
        operators.ne: '!=',
        operators.lt: '<',
        operators.gt: '>',
        operators.le: '<=',
        operators.ge: '>=',
        operators.mul: '*',
        operators.div: '/',
        operators.add: '+',
        operators.sub: '-',
        operators.asc: 'ASC',
        operators.desc: 'DESC',
        'logical-and': '&&',
        'logical-or': '||',
        'RDFTerm-equal': '='
    }
    def __init__(self, select, prefix_map=None):
        self.select = select
        if prefix_map is None:
            prefix_map = {}
        self.prefix_map = prefix_map
        self.namespaces = set([])
        self._string = None
    
    def __unicode__(self):
        if self._string is None:
            self.compile()
        return self._string
    
    def compile(self):
        clauses = []
        clauses.append(' '.join(self.compile_select()))
        clauses.append(' '.join(self.compile_where()))
        clauses[:0] = self.compile_prefixes()
        self._string = '\n'.join(clauses)
        return self._string
    
    def compile_prefix(self, namespace, prefix):
        yield 'PREFIX'
        yield '%s:' % (prefix,)
        yield n3(namespace)
    
    def compile_prefixes(self):
        for namespace, prefix in self.prefix_map.iteritems():
            yield ' '.join(self.compile_prefix(namespace, prefix))
    
    def compile_select(self):
        yield 'SELECT'
        yield ' '.join(self.compile_select_modifiers())
        if '*' in self.select.variables:
            yield '*'
        else:
            yield ' '.join(self.compile_variables(self.select.variables))
        yield ' '.join(self.compile_solution_modifiers())
    
    def compile_select_modifiers(self):
        if self.select._distinct:
            yield self.OPERATORS[Select.distinct]
        elif self.select._reduced:
            yield self.OPERATORS[Select.reduced]
    
    def compile_solution_modifiers(self):
        yield ' '.join(self.compile_order_by())
        if self.select._limit is not None:
            yield 'LIMIT %d' % (self.select._limit,)
        if self.select._offset not in (0, None):
            yield 'OFFSET %d' % (self.select._offset,)
    
    def compile_order_by(self):
        if self.select._order_by:
            yield 'ORDER BY'
            yield ' '.join(self.compile_variables(self.select._order_by))
    
    def compile_variables(self, variables):
        for variable in variables:
            yield ' '.join(self.compile_expression(variable))
    
    def compile_uri(self, uri):
        namespace, fragment = defrag(uri)
        namespace = URIRef(namespace)
        self.namespaces.add(namespace)
        if namespace in self.prefix_map:
            return '%s:%s' % (self.prefix_map[namespace], fragment)
        return n3(uri)
    
    def compile_expression(self, expression):
        if isinstance(expression, URIRef):
            yield self.compile_uri(expression)
        else:
            yield n3(expression)
    
    def compile_where(self):
        yield 'WHERE'
        yield '\n'.join(self.compile_graph_pattern(self.select._where))
    
    def compile_graph_pattern(self, graph_pattern, braces=True):
        if isinstance(graph_pattern, GroupGraphPattern):
            if graph_pattern.optional:
                yield 'OPTIONAL'
                braces = True
        if braces:
            yield '{'
        patterns = list(graph_pattern.patterns)
        while patterns:
            pattern = patterns.pop(0)
            if isinstance(pattern, Triple):
                yield ' '.join(self.compile_variables(pattern))
                if patterns:
                    yield '.'
            elif isinstance(pattern, GraphPattern):
                for token in self.compile_graph_pattern(pattern, False):
                    yield token
                if patterns and token != '}':
                    yield '.'
        if braces:
            yield '}'
    
    def compile_function(self, function):
        operator = self.OPERATORS.get(function.operator, function.operator)
        if isinstance(operator, URIRef) or not isinstance(operator, basestring):
            operator = ' '.join(self.compile_expression(function.operator))
        yield operator
        yield '('
        yield ', '.join(' '.join(self.compile_expression(param)) for param in function.params)
        yield ')'
    
    def execute(self, graph):
        return graph.query(unicode(self))

