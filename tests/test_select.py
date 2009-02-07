#!/usr/bin/env python
import unittest
from rdflib import Variable, Namespace
from telescope.sparql.select import Select

TEST = Namespace('http://www.example.com/test#')
a, b, c = map(Variable, 'abc')

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
        select_where = self.select.where()
        self.assert_(select_where is not self.select)
    
    def test_method_arg_adds_clauses(self):
        select_where = self.select.where(('a', TEST.b, 'c'))
        self.assert_(select_where._where)
    
    def test_optional_kwarg_makes_optional_pattern(self):
        select_where = self.select.where(('a', TEST.b, 'c'), optional=True)
        self.assert_(select_where._where[-1].optional)


if __name__ == '__main__':
    unittest.main()

