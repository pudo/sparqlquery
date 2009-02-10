from rdflib import Literal, URIRef, Namespace
from telescope.sparql import operators
from telescope.sparql.select import *
from telescope.sparql.expressions import *
from telescope.sparql.operators import FunctionCall

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')

def defrag(uri):
    if '#' in uri:
        namespace, fragment = uri.split('#', 1)
        return ('%s#' % namespace, fragment)
    else:
        namespace, fragment = uri.rsplit('/', 1)
        return ('%s/' % namespace, fragment)

class Compiler(object):
    def __init__(self, prefix_map=None):
        if prefix_map is None:
            prefix_map = {}
        self.prefix_map = prefix_map

    def uri(self, uri):
        namespace, fragment = defrag(uri)
        namespace = URIRef(namespace)
        try:
            prefix = self.prefix_map[namespace]
        except KeyError:
            return self.term(uri, False)
        else:
            return '%s:%s' % (prefix, fragment)
    
    def term(self, term, use_prefix=True):
        if term is None:
            return RDF.nil
        elif isinstance(term, Expression):
            if term.operator:
                raise RuntimeError("Found expression with operator; term expected.")
            else:
                return self.term(term.expression)
        elif not hasattr(term, 'n3'):
            return self.term(Literal(term))
        elif use_prefix and isinstance(term, URIRef):
            return self.uri(term)
        elif isinstance(term, Literal):
            if term.datatype in (XSD.int, XSD.float):
                return unicode(term)
        return term.n3()

class ExpressionCompiler(Compiler):
    PRECEDENCE = {
        operators.or_: 0, 'logical-or': 0,
        operators.and_: 1, 'logical-and': 1,
        operators.eq: 2, 'RDFTerm-equal': 2, operators.ne: 2,
        operators.lt: 2, operators.gt: 2, operators.le: 2, operators.ge: 2,
        operators.add: 3, operators.sub: 3, operators.mul: 4, operators.div: 4,
        operators.pos: 5, operators.neg: 5, operators.invert: 5,
        None: 6
    }
    OPERATORS = {
        operators.or_: '||', 'logical-or': '||',
        operators.and_: '&&', 'logical-and': '&&',
        operators.eq: '=', 'RDFTerm-equal': '=', operators.ne: '!=',
        operators.lt: '<', operators.gt: '>',
        operators.le: '<=', operators.ge: '>=',
        operators.add: '+', operators.sub: '-',
        operators.mul: '*', operators.div: '/',
        operators.pos: '+', operators.neg: '-', operators.invert: '!',
    }
    
    def operator(self, expression):
        operator = expression.operator
        if not isinstance(operator, URIRef):
            return self.OPERATORS.get(operator, unicode(operator))
        else:
            return self.uri(operator)
    
    def precedence_lt(self, a, b):
        if isinstance(a, Expression):
            a_precedence = self.PRECEDENCE.get(a.operator)
        else:
            a_precedence = self.PRECEDENCE[None]
        if isinstance(b, Expression):
            b_precedence = self.PRECEDENCE.get(b.operator)
        else:
            b_precedence = self.PRECEDENCE[None]
        return a_precedence < b_precedence
    
    def bracketed(self, expression):
        yield '('
        yield self.compile(expression, False)
        yield ')'
    
    def conditional(self, expression):
        for expr in expression.expressions:
            try:
                operator
            except NameError:
                operator = self.operator(expression)
            else:
                yield operator
            bracketed = self.precedence_lt(expr, expression)
            yield self.compile(expr, bracketed)
        del operator
    
    def binary(self, expression):
        left_bracketed = self.precedence_lt(expression.left, expression)
        right_bracketed = self.precedence_lt(expression.right, expression)
        yield self.compile(expression.left, left_bracketed)
        yield self.operator(expression)
        yield self.compile(expression.right, right_bracketed)
    
    def function(self, expression):
        yield self.operator(expression)
        yield '('
        yield ', '.join(self.compile(arg) for arg in expression.arg_list)
        yield ')'
    
    def unary(self, expression):
        if expression.operator:
            yield self.operator(expression)
        yield self.compile(expression.expression)
    
    def compile(self, expression, bracketed=False):
        if not bracketed:
            if isinstance(expression, ConditionalExpression):
                return ' '.join(self.conditional(expression))
            elif isinstance(expression, BinaryExpression):
                return ' '.join(self.binary(expression))
            elif isinstance(expression, FunctionCall):
                return ''.join(self.function(expression))
            elif isinstance(expression, Expression):
                return ''.join(self.unary(expression))
            else:
                return self.term(expression)
        else:
            return ''.join(self.bracketed(expression))

class SelectCompiler(Compiler):
    EXPRESSION_COMPILER = ExpressionCompiler()
    
    def expression(self, expression, bracketed=False):
        yield self.EXPRESSION_COMPILER.compile(expression, bracketed)
    
    def compile(self, select):
        return '\n'.join(self.clauses(select))
    
    def clauses(self, select):
        for prefix in self.prefixes():
            yield prefix
        yield ' '.join(self.select(select))
        yield ' '.join(self.where(select))
        yield ' '.join(self.order_by(select))
        yield ' '.join(self.limit(select))
        yield ' '.join(self.offset(select))
    
    def prefixes(self):
        for namespace, prefix in self.prefix_map.iteritems():
            yield ' '.join(self.prefix(prefix, namespace))
    
    def prefix(self, prefix, namespace):
        yield 'PREFIX'
        yield '%s:' % (prefix,)
        yield self.term(namespace, False)
    
    def select(self, select):
        yield 'SELECT'
        yield ' '.join(self.unique(select))
        yield ' '.join(self.projection(select))
    
    def unique(self, select):
        if select._distinct:
            yield 'DISTINCT'
        elif select._reduced:
            yield 'REDUCED'
    
    def limit(self, select):
        if select._limit is not None:
            yield 'LIMIT %d' % (select._limit,)
    
    def offset(self, select):
        if select._offset not in (0, None):
            yield 'OFFSET %d' % (select._offset,)
    
    def order_by(self, select):
        if select._order_by:
            yield 'ORDER BY'
            for expression in select._order_by:
                yield self.expression(expression)
    
    def projection(self, select):
        if '*' in select.variables:
            yield '*'
        else:
            for variable in select.variables:
                yield self.term(variable)
    
    def where(self, select):
        yield 'WHERE'
        yield '\n'.join(self.graph_pattern(select._where))
    
    def triple(self, triple):
        subject, predicate, object = triple
        yield self.term(subject)
        yield self.term(predicate)
        yield self.term(object)
    
    def graph_pattern(self, graph_pattern, braces=True):
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
                yield ' '.join(self.triple(pattern))
                if patterns or filters:
                    yield '.'
            elif isinstance(pattern, UnionGraphPattern):
                for union_pattern in pattern.patterns:
                    try:
                        union_sep
                    except NameError:
                        union_sep = 'UNION'
                    else:
                        yield union_sep
                    yield ' '.join(self.graph_pattern(union_pattern, True))
                del union_sep
            elif isinstance(pattern, GraphPattern):
                token = None
                for token in self.graph_pattern(pattern, False):
                    yield token
                if token != '}' and (patterns or filters):
                    yield '.'
        while filters:
            filter = filters.pop(0)
            yield ' '.join(self.filter(filter))
            if filters:
                yield '.'
        if braces:
            yield '}'
    
    def filter(self, filter):
        yield 'FILTER'
        bracketed = isinstance(filter.constraint,
            (ConditionalExpression, BinaryExpression))
        yield ' '.join(self.expression(filter.constraint, bracketed))
