from rdflib import Literal, URIRef, Namespace
from telescope.sparql import operators
from telescope.sparql.select import Select, Triple, GraphPattern, GroupGraphPattern
from telescope.sparql.expressions import *
from telescope.sparql.operators import FunctionCall

XSD = Namespace('http://www.w3.org/2001/XMLSchema#')


def literal(term):
    if not hasattr(term, 'n3'):
        return literal(Literal(term))
    elif isinstance(term, Literal):
        if term.datatype in (XSD.int, XSD.float):
            return unicode(term)
    return term.n3()

def defrag(uri):
    if '#' in uri:
        namespace, fragment = uri.split('#', 1)
        return ('%s#' % namespace, fragment)
    return (uri, None)

class SelectCompiler(object):
    PRECEDENCE = {
        operators.or_: 0,
        operators.and_: 1,
        operators.eq: 2,
        operators.ne: 2,
        operators.lt: 2,
        operators.gt: 2,
        operators.le: 2,
        operators.ge: 2,
        operators.add: 3,
        operators.sub: 3,
        operators.mul: 4,
        operators.div: 4,
        operators.pos: 5,
        operators.neg: 5,
        operators.invert: 5,
        'logical-and': 1,
        'logical-or': 0,
        'RDFTerm-equal': 2
    }
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
        yield literal(namespace)
    
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
        return literal(uri)
    
    def compile_operator(self, operator):
        return self.OPERATORS.get(operator, unicode(operator))

    def compile_expression(self, expression, precedence=0):
        if isinstance(expression, URIRef):
            yield self.compile_uri(expression)
        elif isinstance(expression, ConditionalExpression):
            operator = self.compile_operator(expression.operator)
            expressions = iter(expression.expressions)
            for expr in expressions:
                yield ' '.join(self.compile_expression(expr))
                break
            for expr in expressions:
                yield operator
                yield ' '.join(self.compile_expression(expr))
        elif isinstance(expression, BinaryExpression):
            yield ' '.join(self.compile_expression(expression.left))
            yield self.OPERATORS.get(expression.operator, unicode(expression.operator))
            yield ' '.join(self.compile_expression(expression.right))
        elif isinstance(expression, FunctionCall):
            function = self.OPERATORS.get(expression.operator, unicode(expression.operator))
            if isinstance(function, URIRef):
                function = self.compile_uri(function)
            arg_list = [' '.join(self.compile_expression(arg)) for arg in expression.arg_list]
            yield '%s(%s)' % (function, ', '.join(arg_list))
        elif isinstance(expression, Expression):
            if expression.operator:
                operator = self.OPERATORS.get(expression.operator, unicode(expression.operator))
            else:
                operator = ''
            yield '%s%s' % (operator, ' '.join(self.compile_expression(expression.expression)))
        else:
            yield literal(expression)
    
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
        filters = list(graph_pattern.filters)
        while patterns:
            pattern = patterns.pop(0)
            if isinstance(pattern, Triple):
                yield ' '.join(self.compile_variables(pattern))
                if patterns or filters:
                    yield '.'
            elif isinstance(pattern, GraphPattern):
                for token in self.compile_graph_pattern(pattern, False):
                    yield token
                if token != '}' and (patterns or filters):
                    yield '.'
        while filters:
            filter = filters.pop(0)
            yield ' '.join(self.compile_filter(filter))
            if filters:
                yield '.'
        if braces:
            yield '}'
    
    def compile_filter(self, filter):
        yield 'FILTER'
        if isinstance(filter.constraint, BinaryExpression):
            yield '(%s)' % ' '.join(self.compile_expression(filter.constraint))
        else:
            yield ' '.join(self.compile_expression(filter.constraint))

    def execute(self, graph):
        return graph.query(unicode(self))

