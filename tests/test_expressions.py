#!/usr/bin/env python
import unittest
from rdflib import Variable
from telescope.sparql.expressions import *
from telescope.sparql.operators import Operator, FunctionCall, op
from telescope.sparql.util import v, to_variable

class TestExpressions(unittest.TestCase):
    def test_logical_returns_conditional_expression(self):
        self.assertType(ConditionalExpression, Expression(2) | 1)
        self.assertType(ConditionalExpression, Expression(2) & 1)
    
    def test_comparison_returns_binary_expression(self):
        self.assertType(BinaryExpression, Expression(2) > 1)
        self.assertType(BinaryExpression, Expression(2) == 1)
        self.assertType(BinaryExpression, Expression(2) < 1)
        self.assertType(BinaryExpression, Expression(2) >= 1)
        self.assertType(BinaryExpression, Expression(2) <= 1)
        self.assertType(BinaryExpression, Expression(2) != 1)
        self.assertType(BinaryExpression, Expression(2) * 1)
        self.assertType(BinaryExpression, Expression(2) + 1)
        self.assertType(BinaryExpression, Expression(2) - 1)
        self.assertType(BinaryExpression, Expression(2) / 1)
    
    def assertType(self, class_, obj):
        return self.assert_(isinstance(obj, class_))

class TestVariableExpressions(unittest.TestCase):
    def test_getattr_returns_variable_expression(self):
        foo = v.foo
        self.assert_(isinstance(foo, Expression))
        variable_foo = to_variable(foo)
        self.assert_(isinstance(variable_foo, Variable))
        self.assertEqual(variable_foo, Variable('foo'))

    def test_getitem_returns_variable_expression(self):
        foo = v['foo']
        self.assert_(isinstance(foo, Expression))
        variable_foo = to_variable(foo)
        self.assert_(isinstance(variable_foo, Variable))
        self.assertEqual(variable_foo, Variable('foo'))

if __name__ == '__main__':
    unittest.main()
