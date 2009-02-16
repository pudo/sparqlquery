from operator import itemgetter
from rdflib import Literal, URIRef, Namespace
from telescope.sparql.expressions import *
from telescope.sparql import operators
from telescope.sparql.operators import FunctionCall
from telescope.sparql.patterns import *
from telescope.sparql.select import *
from telescope.sparql.helpers import RDF, XSD, is_a
from telescope.sparql.util import defrag, to_variable, to_list

__all__ = ['Compiler', 'ExpressionCompiler', 'SelectCompiler']

def join(tokens, sep=' '):
    return sep.join([unicode(token) for token in tokens if token])

class Compiler(object):
    def __init__(self, prefix_map=None):
        if prefix_map is None:
            prefix_map = {}
        self.prefix_map = prefix_map

class ExpressionCompiler(Compiler):
    PRECEDENCE = {
        operators.or_: 0, 'logical-or': 0,
        operators.and_: 1, 'logical-and': 1,
        operators.eq: 2, 'RDFTerm-equal': 2, operators.ne: 2,
        operators.lt: 2, operators.gt: 2, operators.le: 2, operators.ge: 2,
        operators.add: 3, operators.sub: 3, operators.mul: 4, operators.div: 4,
        operators.pos: 5, operators.neg: 5,
        operators.invert: 5, operators.inv: 5
    }
    DEFAULT_PRECEDENCE = 6
    OPERATORS = {
        operators.or_: '||', 'logical-or': '||',
        operators.and_: '&&', 'logical-and': '&&',
        operators.eq: '=', 'RDFTerm-equal': '=', operators.ne: '!=',
        operators.lt: '<', operators.gt: '>',
        operators.le: '<=', operators.ge: '>=',
        operators.add: '+', operators.sub: '-',
        operators.mul: '*', operators.div: '/',
        operators.pos: '+', operators.neg: '-',
        operators.invert: '!', operators.inv: '!'
    }
    
    def compile(self, expression, bracketed=False):
        if not bracketed:
            if isinstance(expression, ConditionalExpression):
                return join(self.conditional(expression))
            elif isinstance(expression, BinaryExpression):
                return join(self.binary(expression))
            elif isinstance(expression, FunctionCall):
                return join(self.function(expression), '')
            elif isinstance(expression, Expression):
                return join(self.unary(expression), '')
            else:
                return self.term(expression)
        else:
            return join(self.bracketed(expression), '')
    
    def get_precedence(self, obj):
        if isinstance(obj, Expression):
            return self.PRECEDENCE.get(obj.operator, self.DEFAULT_PRECEDENCE)
        return self.DEFAULT_PRECEDENCE
    
    def precedence_lt(self, a, b):
        return self.get_precedence(a) < self.get_precedence(b)
    
    def uri(self, uri):
        if uri is not is_a:
            namespace, fragment = defrag(uri)
            namespace = URIRef(namespace)
            try:
                prefix = self.prefix_map[namespace]
            except KeyError:
                return self.term(uri, False)
            else:
                return '%s:%s' % (prefix, fragment)
        else:
            return 'a'
    
    def term(self, term, use_prefix=True):
        if term is None:
            return RDF.nil
        elif not hasattr(term, 'n3'):
            return self.term(Literal(term))
        elif use_prefix and isinstance(term, URIRef):
            return self.uri(term)
        elif isinstance(term, Literal):
            if term.datatype in (XSD.int, XSD.integer, XSD.float, XSD.boolean):
                return unicode(term).lower()
        return term.n3()
    
    def operator(self, operator):
        token = self.OPERATORS.get(operator)
        if token:
            return token
        elif isinstance(operator, URIRef):
            return self.uri(operator)
        else:
            return unicode(operator)
    
    def bracketed(self, expression):
        yield '('
        yield self.compile(expression, False)
        yield ')'
    
    def conditional(self, expression):
        operator = self.operator(expression.operator)
        for i, expr in enumerate(expression.operands):
            if i:
                yield operator
            bracketed = self.precedence_lt(expr, expression)
            yield self.compile(expr, bracketed)
    
    def binary(self, expression):
        left_bracketed = self.precedence_lt(expression.left, expression)
        right_bracketed = self.precedence_lt(expression.right, expression)
        yield self.compile(expression.left, left_bracketed)
        yield self.operator(expression.operator)
        yield self.compile(expression.right, right_bracketed)
    
    def function(self, expression):
        yield self.operator(expression.operator)
        yield '('
        yield join([self.compile(arg) for arg in expression.arg_list], ', ')
        yield ')'
    
    def unary(self, expression):
        if expression.operator:
            yield self.operator(expression.operator)
        yield self.compile(expression.value)

class SelectCompiler(Compiler):
    def __init__(self, prefix_map=None):
        Compiler.__init__(self, prefix_map)
        self.expression_compiler = ExpressionCompiler(self.prefix_map)
    
    def compile(self, select):
        """Compile `select` and return the resulting string.
        
        `select` is a `telescope.sparql.select.Select` instance.
        
        """
        return join(self.clauses(select), '\n')
    
    def expression(self, expression, bracketed=False):
        """
        Compile `expression` with this instance's `expression_compiler` and
        return (not yield) the resulting string.
        
        If `bracketed` is true, the resulting string will be enclosed in
        parentheses.
        
        """
        return self.expression_compiler.compile(expression, bracketed)
    
    def clauses(self, select):
        for prefix in self.prefixes():
            yield prefix
        yield join(self.select(select))
        yield join(self.where(select))
        yield join(self.order_by(select))
        yield join(self.limit(select))
        yield join(self.offset(select))
    
    def prefixes(self):
        prefixes = sorted(self.prefix_map.iteritems(), key=itemgetter(1))
        for namespace, prefix in prefixes:
            yield join(self.prefix(prefix, namespace))
    
    def prefix(self, prefix, namespace):
        yield 'PREFIX'
        yield '%s:' % (prefix,)
        yield self.expression_compiler.term(namespace, False)
    
    def select(self, select):
        yield 'SELECT'
        yield join(self.unique(select))
        yield join(self.projection(select))
    
    def unique(self, select):
        if select._distinct:
            yield 'DISTINCT'
        elif select._reduced:
            yield 'REDUCED'
    
    def limit(self, select):
        if select._limit is not None:
            yield 'LIMIT'
            yield select._limit
    
    def offset(self, select):
        if select._offset not in (0, None):
            yield 'OFFSET'
            yield select._offset
    
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
                yield self.expression(variable)
    
    def where(self, select):
        yield 'WHERE'
        yield join(self.graph_pattern(select._where))
    
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
                yield join(self.triple(pattern))
                if patterns or filters:
                    yield '.'
            elif isinstance(pattern, TriplesSameSubject):
                yield join(self.triples_same_subject(pattern))
                if patterns or filters:
                    yield '.'
            elif isinstance(pattern, UnionGraphPattern):
                for i, alternative in enumerate(pattern.patterns):
                    if i:
                        yield 'UNION'
                    yield join(self.graph_pattern(alternative, True))
            elif isinstance(pattern, GraphPattern):
                token = None
                for token in self.graph_pattern(pattern, False):
                    yield token
                if token != '}' and (patterns or filters):
                    yield '.'
        while filters:
            filter = filters.pop(0)
            yield join(self.filter(filter))
            if filters:
                yield '.'
        if braces:
            yield '}'
    
    def triple(self, triple):
        subject, predicate, object = triple
        yield self.expression(subject)
        yield self.expression(predicate)
        yield self.expression(object)
    
    def triples_same_subject(self, triples):
        yield self.expression(triples.subject)
        yield join(self.predicate_object_list(triples.predicate_object_list))
    
    def predicate_object_list(self, predicate_object_list):
        for i, (predicate, object_list) in enumerate(predicate_object_list):
            if i:
                yield ';'
            yield self.expression(predicate)
            for j, object in enumerate(to_list(object_list)):
                if j:
                    yield ','
                yield self.expression(object)
    
    def filter(self, filter):
        yield 'FILTER'
        constraint = filter.constraint
        bracketed = False
        while isinstance(constraint, ConditionalExpression):
            if len(constraint.operands) == 1:
                constraint = constraint.operands[0]
            else:
                break
        if not isinstance(constraint, FunctionCall):
            bracketed = True
        yield self.expression(constraint, bracketed)
