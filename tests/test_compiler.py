#!/usr/bin/env python
import re
from nose.tools import assert_raises, assert_equal
from rdflib import Variable, Namespace, Literal
from telescope.sparql.expressions import Expression
from telescope.sparql import operators
from telescope.sparql.operators import Operator, FunctionCall
from telescope.sparql.patterns import *
from telescope.sparql.select import Select
from telescope.sparql.compiler import *
from telescope.sparql.helpers import *
import helpers

EX = Namespace('http://example.org/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DC10 = Namespace('http://purl.org/dc/elements/1.0/')
DC11 = Namespace('http://purl.org/dc/elements/1.1/')

def tokens_equal(output, *expected):
    if isinstance(output, basestring):
        output = output.split()
    tokens = []
    for arg in expected:
        if isinstance(arg, basestring):
            arg = arg.split()
        tokens.extend(arg)
    output = " ".join(output)
    expected = " ".join(tokens)
    assert_equal(output, expected)
    return True

class TestCompilingTerm:
    def setup(self):
        self.compiler = ExpressionCompiler()
    
    def test_compiling_none_returns_nil(self):
        assert self.compiler.compile(None) == RDF.nil
    
    def test_compiling_is_a_helper_returns_keyword_a(self):
        term = is_a
        assert self.compiler.compile(term) == 'a'
    
    def test_compiling_uri_returns_absolute_n3_iri(self):
        term = FOAF.Person
        assert self.compiler.compile(term) == term.n3()
    
    def test_compiling_non_n3_compiles_literal(self):
        value = 'a'
        literal = Literal(value)
        assert self.compiler.compile(value) == self.compiler.compile(literal)
    
    def test_compiling_integer_omits_datatype(self):
        assert self.compiler.compile(10) == '10'
    
    def test_compiling_float_omits_datatype(self):
        assert self.compiler.compile(10.5) == '10.5'
    
    def test_compiling_term_with_bracketed_true_outputs_brackets(self):
        assert tokens_equal(self.compiler.compile(1, bracketed=True), '(1)')

class CompilingExpressionBase:
    def setup(self):
        self.compiler = ExpressionCompiler({RDF: 'rdf', FOAF: 'foaf'})

class TestCompilingTermWithPrefixMap(CompilingExpressionBase):
    def setup(self):
        self.compiler = ExpressionCompiler({FOAF: 'foaf'})
    
    def test_compiling_uri_returns_prefixed_name(self):
        term = FOAF.Person
        assert self.compiler.term(term) == 'foaf:Person'
    
    def test_compiling_uri_without_prefix_returns_absolute_n3_iri(self):
        term = XSD.integer
        assert self.compiler.term(term) == term.n3()

class TestCompilingOperator(CompilingExpressionBase):
    def test_compiling_unary_operator_outputs_token(self):
        for op in helpers.UNARY_OPERATORS:
            token = self.compiler.OPERATORS[op]
            assert tokens_equal(self.compiler.operator(op), token)
    
    def test_compiling_binary_operator_outputs_token(self):
        for op in helpers.BINARY_OPERATORS:
            token = self.compiler.OPERATORS[op]
            assert tokens_equal(self.compiler.operator(op), token)
    
    def test_compiling_conditional_operator_outputs_token(self):
        for op in helpers.CONDITIONAL_OPERATORS:
            token = self.compiler.OPERATORS[op]
            assert tokens_equal(self.compiler.operator(op), token)
    
    def test_compiling_builtin_operator_outputs_name(self):
        for op in helpers.BUILTIN_OPERATORS:
            token = self.compiler.OPERATORS.get(op, op)
            assert tokens_equal(self.compiler.operator(op), token)
    
    def test_compiling_extension_function_outputs_uri(self):
        operator = FN.ceiling
        token = operator.n3()
        assert tokens_equal(self.compiler.operator(operator), token)

class TestCompilingConditional(CompilingExpressionBase):
    def test_compiling_ored_ands_omits_brackets(self):
        expr = or_(and_(1, 2), 3)
        assert tokens_equal(self.compiler.compile(expr), '1 && 2 || 3')
        expr = or_(1, and_(2, 3))
        assert tokens_equal(self.compiler.compile(expr), '1 || 2 && 3')
        expr = or_(and_(1, 2), and_(3, 4))
        assert tokens_equal(self.compiler.compile(expr), '1 && 2 || 3 && 4')
    
    def test_compiling_anded_ors_includes_brackets(self):
        expr = and_(or_(1, 2), 3)
        assert tokens_equal(self.compiler.compile(expr), '(1 || 2) && 3')
        expr = and_(1, or_(2, 3))
        assert tokens_equal(self.compiler.compile(expr), '1 && (2 || 3)')
        expr = and_(or_(1, 2), or_(3, 4))
        assert tokens_equal(self.compiler.compile(expr), '(1 || 2) && (3 || 4)')
    
    def test_compiling_anded_operators_omits_brackets(self):
        expr = or_(op.bound(v.name), op.bound(v.mbox))
        output = self.compiler.compile(expr)
        assert tokens_equal(output, 'bound(?name) || bound(?mbox)')
    
    def test_compiling_ored_operators_omits_brackets(self):
        expr = and_(op.bound(v.name), op.bound(v.mbox))
        output = self.compiler.compile(expr)
        assert tokens_equal(output, 'bound(?name) && bound(?mbox)')

class TestCompilingRelationalExpression(CompilingExpressionBase):
    def test_compiling_unary_expression_outputs_operator_and_operand(self):
        for op in helpers.UNARY_OPERATORS:
            expr = op(v.x)
            token = self.compiler.OPERATORS[op]
            assert tokens_equal(self.compiler.compile(expr), '%s?x' % token)
    
    def test_compiling_binary_expression_outputs_operator_and_operands(self):
        for op in helpers.BINARY_OPERATORS:
            expr = op(v.x, 2)
            token = self.compiler.OPERATORS[op]
            output = self.compiler.compile(expr)
            assert tokens_equal(output, '?x %s 2' % token)

class BaseCompilingSelect:
    PREFIXES = "PREFIX foaf: <http://xmlns.com/foaf/0.1/>"
    
    def setup(self):
        self.compiler = SelectCompiler({FOAF: 'foaf'})

class TestCompilingTriple(BaseCompilingSelect):
    def test_compiling_triple_outputs_three_terms(self):
        triple = (v.x, FOAF.name, "Brian")
        assert tokens_equal(
            self.compiler.triple(triple), '?x foaf:name "Brian"')

class TestCompilingSelectModifiers(BaseCompilingSelect):
    def test_compiling_distinct_outputs_distinct_keyword(self):
        select = Select([v.x]).distinct()
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            'SELECT DISTINCT ?x WHERE { }'
        )
    
    def test_compiling_reduced_outputs_reduced_keyword(self):
        select = Select([v.x]).reduced()
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            'SELECT REDUCED ?x WHERE { }'
        )

    def test_compiling_limit_outputs_limit_clause(self):
        select = Select([v.x]).limit(5)
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            'SELECT ?x WHERE { } LIMIT 5'
        )

    def test_compiling_offset_outputs_offset_clause(self):
        select = Select([v.x]).offset(10)
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            'SELECT ?x WHERE { } OFFSET 10'
        )

    def test_compiling_order_by_outputs_order_by_clause(self):
        select = Select([v.x]).order_by(v.x)
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            'SELECT ?x WHERE { } ORDER BY ?x'
        )


class TestCompilingSelect(BaseCompilingSelect):
    def test_compiling_select_all_outputs_select_all(self):
        select = Select(['*'])
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES, 'SELECT * WHERE { }'
        )
    
    def test_compiling_default_outputs_empty_graph_pattern(self):
        select = Select([v.x])
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES, 'SELECT ?x WHERE { }'
        )
    
    def test_compiling_where_outputs_basic_graph_pattern(self):
        select = Select([v.name, v.mbox]).where(
            (v.x, FOAF.name, v.name), (v.x, FOAF.mbox, v.mbox)
        )
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            """
            SELECT ?name ?mbox WHERE {
                ?x foaf:name ?name .
                ?x foaf:mbox ?mbox
            }
            """
        )
    
    def test_compiling_where_outputs_optional_graph_pattern(self):
        select = Select([v.name, v.mbox]).where(
            (v.x, FOAF.name, v.name),
            optional((v.x, FOAF.mbox, v.mbox))
        )
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            """
            SELECT ?name ?mbox WHERE {
                ?x foaf:name ?name .
                OPTIONAL { ?x foaf:mbox ?mbox }
            }
            """
        )
    
    def test_compiling_where_outputs_union_graph_pattern(self):
        select = Select([v.title]).where(union(
            [(v.book, DC10['title'], v.title)],
            [(v.book, DC11['title'], v.title)]
        ))
        compiler = SelectCompiler({DC10: 'dc10', DC11: 'dc11'})
        assert tokens_equal(
            compiler.compile(select),
            """
            PREFIX dc10: <http://purl.org/dc/elements/1.0/>
            PREFIX dc11: <http://purl.org/dc/elements/1.1/>
            SELECT ?title WHERE {
                { ?book dc10:title ?title } UNION { ?book dc11:title ?title }
            }
            """
        )
    
    def test_compiling_filter_outputs_filter(self):
        select = Select([v.x]).where(
            (v.x, FOAF.name, v.name), (v.x, FOAF.mbox, v.mbox)
        ).filter(op.regex(v.name, "Smith"))
        
        assert tokens_equal(
            self.compiler.compile(select), self.PREFIXES,
            """
            SELECT ?x WHERE {
                ?x foaf:name ?name .
                ?x foaf:mbox ?mbox .
                FILTER regex(?name, "Smith")
            }
            """
        )
