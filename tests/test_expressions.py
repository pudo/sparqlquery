#!/usr/bin/env python
import unittest
from telescope.sparql.expressions import *
from telescope.sparql.operators import Operator, FunctionCall, op

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

if __name__ == '__main__':
    unittest.main()
