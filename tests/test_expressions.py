#!/usr/bin/env python
import unittest
from telescope.sparql.expressions import *
from telescope.sparql.operators import Operator, FunctionCall, op

class TestExpressions(unittest.TestCase):
    def test_logical_returns_conditional_expression(self):
        self.assertIsConditionalExpression(Expression(2) | 1)
        self.assertIsConditionalExpression(Expression(2) & 1)
        
    def test_comparison_returns_binary_expression(self):
        self.assertIsBinaryExpression(Expression(2) > 1)
        self.assertIsBinaryExpression(Expression(2) == 1)
        self.assertIsBinaryExpression(Expression(2) < 1)
        self.assertIsBinaryExpression(Expression(2) >= 1)
        self.assertIsBinaryExpression(Expression(2) <= 1)
        self.assertIsBinaryExpression(Expression(2) != 1)
        self.assertIsBinaryExpression(Expression(2) * 1)
        self.assertIsBinaryExpression(Expression(2) + 1)
        self.assertIsBinaryExpression(Expression(2) - 1)
        self.assertIsBinaryExpression(Expression(2) / 1)
    
    def assertIsExpression(self, obj):
        return self.assert_(isinstance(obj, Expression))
    
    def assertIsBinaryExpression(self, obj):
        return self.assert_(isinstance(obj, BinaryExpression))
    
    def assertIsConditionalExpression(self, obj):
        return self.assert_(isinstance(obj, ConditionalExpression))

if __name__ == '__main__':
    unittest.main()
