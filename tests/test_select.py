#!/usr/bin/env python
import unittest
from rdflib import Variable, Namespace
from telescope.sparql.select import Select
from telescope.sparql.expressions import Expression
from telescope.sparql.operators import op

TEST = Namespace('http://www.example.com/test#')
a, b, c, x, y, z = map(Variable, 'abcxyz')

class TestSelectVariables(unittest.TestCase):
    def setUp(self):
        self.select = Select([a])
    
    def test_variables_arg_adds_variables(self):
        self.assert_(a in self.select.variables)
    
    def test_method_is_generative(self):
        select = self.select.select(b)
        self.assert_(select is not self.select)
    
    def test_method_args_add_variables(self):
        select = self.select.select(b, c)
        self.assert_(a in select.variables)
        self.assert_(b in select.variables)
        self.assert_(c in select.variables)

class TestSelectWhere(unittest.TestCase):
    def setUp(self):
        self.select = Select([])
    
    def test_default_has_no_clauses(self):
        self.assert_(not self.select._where)
    
    def test_patterns_arg_adds_clauses(self):
        select = Select([], ('a', TEST.b, 'c'))
        self.assert_(select._where)
    
    def test_method_is_generative(self):
        select = self.select.where()
        self.assert_(select is not self.select)
    
    def test_method_args_add_clauses(self):
        select = self.select.where(('a', TEST.b, 'c'), ('x', TEST.y, 'z'))
        self.assert_(len(select._where[0].patterns) == 2)
    
    def test_optional_kwarg_makes_optional_pattern(self):
        select = self.select.where(('a', TEST.b, 'c'), optional=True)
        self.assert_(select._where[-1].optional)

class TestSelectfilter(unittest.TestCase):
    def setUp(self):
        self.select = Select([])
    
    def test_method_is_generative(self):
        select = self.select.filter()
        self.assert_(select is not self.select)

    def test_method_args_add_filters(self):
        select = self.select.filter(Expression(2) > 1, Expression('z') > 'a')
        self.assert_(select._where.filters)

if __name__ == '__main__':
    unittest.main()

