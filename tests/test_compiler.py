#!/usr/bin/env python
import re
import unittest
from rdflib import Variable, Namespace
from telescope.sparql.select import Select
from telescope.sparql.compiler import SelectCompiler
from telescope.sparql.expressions import Expression, or_, and_
from telescope.sparql import operators

TEST = Namespace('http://www.example.com/test#')
a, b, c, x, y, z = map(Variable, 'abcxyz')

def normalize(text):
    return re.sub(r'\s+', ' ', unicode(text).strip())

class TestSelectCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = SelectCompiler()
    
    def test_select_empty_graph_pattern_output(self):
        select = Select([a])
        self.assertEquivalent(self.compiler.compile(select),
            'SELECT ?a WHERE { }'
        )
    
    def test_select_basic_graph_pattern_output(self):
        select = Select([a]).where((a, TEST.b, 'c'))
        self.assertEquivalent(self.compiler.compile(select),
            'SELECT ?a WHERE { ?a <http://www.example.com/test#b> "c" }'
        )
        select = select.where((a, TEST.y, 'z'))
        self.assertEquivalent(self.compiler.compile(select),
            """SELECT ?a WHERE {
            ?a <http://www.example.com/test#b> "c" .
            ?a <http://www.example.com/test#y> "z"
            }"""
        )

    def test_select_optional_graph_pattern_output(self):
        select = Select([a]).where((a, TEST.b, 'c'), optional=True)
        self.assertEquivalent(self.compiler.compile(select),
            """SELECT ?a WHERE {
            OPTIONAL { ?a <http://www.example.com/test#b> "c" }
            }"""
        )
        select = select.where((x, TEST.y, z), (z, TEST.y, a), optional=True)
        self.assertEquivalent(self.compiler.compile(select),
            """SELECT ?a WHERE {
            OPTIONAL { ?a <http://www.example.com/test#b> "c" }
            OPTIONAL {
                ?x <http://www.example.com/test#y> ?z .
                ?z <http://www.example.com/test#y> ?a
            } }"""
        )

    def test_select_multiple_graph_patterns_output(self):
        select = Select([a, z], (a, TEST.b, 'c')).where((a, TEST.y, z), optional=True)
        self.assertEquivalent(self.compiler.compile(select),
            """SELECT ?a ?z WHERE {
            ?a <http://www.example.com/test#b> "c" .
            OPTIONAL { ?a <http://www.example.com/test#y> ?z }
            }"""
        )
        select = select.where((x, TEST.y, z), (b, TEST.x, 'y')).where((z, TEST.b, 'a'), optional=True)
        self.assertEquivalent(self.compiler.compile(select),
            """SELECT ?a ?z WHERE {
            ?a <http://www.example.com/test#b> "c" .
            OPTIONAL { ?a <http://www.example.com/test#y> ?z }
            ?x <http://www.example.com/test#y> ?z .
            ?b <http://www.example.com/test#x> "y" .
            OPTIONAL { ?z <http://www.example.com/test#b> "a" }
            }"""
        )
    
    def test_binary_conditional_expression_output(self):
        compiler = self.compiler.EXPRESSION_COMPILER
        for operator in (operators.and_, operators.or_):
            expr = operator(Expression(2), 1)
            token = compiler.OPERATORS.get(operator)
            self.assertEquivalent(compiler.compile(expr), '2 %s 1' % (token,))
    
    def test_arbitrary_conditional_expression_output(self): 
        compiler = self.compiler.EXPRESSION_COMPILER
        expr = or_(1, 2, 3, 4, 5)
        self.assertEquivalent(compiler.compile(expr), '1 || 2 || 3 || 4 || 5')
        expr = and_(1, 2, 3, 4, 5)
        self.assertEquivalent(compiler.compile(expr), '1 && 2 && 3 && 4 && 5')
    
    def test_nested_conditional_expression_output(self):
        compiler = self.compiler.EXPRESSION_COMPILER
        expr = and_(1, or_(2, 3))
        self.assertEquivalent(compiler.compile(expr), '1 && (2 || 3)')
    
    def test_binary_expression_output(self):
        compiler = self.compiler.EXPRESSION_COMPILER
        for operator in (
            operators.eq, operators.ne, operators.lt, operators.gt,
            operators.le, operators.ge, operators.mul, operators.div,
            operators.add, operators.sub):
            expr = operator(Expression(2), 1)
            token = compiler.OPERATORS.get(operator)
            self.assertEquivalent(compiler.compile(expr), '2 %s 1' % (token,))
    
    def test_unary_expression_output(self):
        compiler = self.compiler.EXPRESSION_COMPILER
        for operator in (operators.invert, operators.pos, operators.neg):
            expr = operator(Expression(2))
            token = compiler.OPERATORS.get(operator)
            self.assertEquivalent(compiler.compile(expr), '%s2' % (token,))
    
    def test_function_call_output(self):
        compiler = self.compiler.EXPRESSION_COMPILER
        op = operators.Operator('sameTerm')
        op_call = op(1, "two")
        self.assertEquivalent(compiler.compile(op_call), 'sameTerm(1, "two")')
    
    def test_select_single_filter_output(self):
        select = Select([a]).filter(Expression(a) > 1)
        self.assertEquivalent(self.compiler.compile(select),
            'SELECT ?a WHERE { FILTER (?a > 1) }'
        )
    
    def test_select_multiple_filters_output(self):
        select = Select([a]).filter(Expression(a) > 0, Expression(a) <= 5)
        self.assertEquivalent(self.compiler.compile(select),
            'SELECT ?a WHERE { FILTER (?a > 0 && ?a <= 5) }'
        )
    
    def assertEquivalent(self, output, expected):
        if not isinstance(output, basestring):
            output = ' '.join(output)
        return self.assertEqual(normalize(output), normalize(expected))

if __name__ == '__main__':
    unittest.main()

