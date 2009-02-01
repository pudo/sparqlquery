#!/usr/bin/env python
import unittest
from rdflib import Variable
from telescope.sparql.select import Select

class TestLimit(unittest.TestCase):
    def setUp(self):
        self.select = Select([])
    
    def test_limit_defaults_to_none(self):
        self.assertEqual(self.select._limit, None)
    
    def test_limit_in_kwarg(self):
        select = Select([], limit=5)
        self.assertEqual(select._limit, 5)
    
    def test_limit_in_slice(self):
        select = self.select[:10]
        self.assertEqual(select._limit, 10)
        select = select[10:50]
        self.assertEqual(select._limit, 40)
    
    def test_limit_method(self):
        select = self.select.limit(10)
        self.assertEqual(select._limit, 10)

    def test_method_is_generative(self):
        select = self.select.limit(10)
        self.assert_(select is not self.select)

class TestOffset(unittest.TestCase):
    def setUp(self):
        self.select = Select([])
    
    def test_offset_defaults_to_none(self):
        self.assertEqual(self.select._offset, None)
    
    def test_offset_in_kwarg(self):
        select = Select([], offset=5)
        self.assertEqual(select._offset, 5)
    
    def test_offset_in_slice(self):
        select = self.select[:10]
        self.assertEqual(select._offset, None)
        select = select[10:50]
        self.assertEqual(select._offset, 10)
    
    def test_offset_method(self):
        select = self.select.offset(10)
        self.assertEqual(select._offset, 10)
    
    def test_method_is_generative(self):
        select = self.select.offset(10)
        self.assert_(select is not self.select)

class TestDistinct(unittest.TestCase):
    def setUp(self):
        self.select = Select([])
    
    def test_distinct_defaults_to_false(self):
        self.assertEqual(self.select._distinct, False)

    def test_distinct_in_kwarg(self):
        select = Select([], distinct=True)
        self.assertEqual(select._distinct, True)
    
    def test_distinct_method(self):
        select = self.select.distinct()
        self.assertEqual(select._distinct, True)
        select = select.distinct(False)
        self.assertEqual(select._distinct, False)
    
    def test_method_is_generative(self):
        select = self.select.distinct()
        self.assert_(select is not self.select)
    
    def test_mutually_exclusive_with_reduced(self):
        self.assertRaises(ValueError, Select, [], distinct=True, reduced=True)
        select = Select([], reduced=True).distinct()
        self.assertEqual(select._reduced, False)

class TestReduced(unittest.TestCase):
    def setUp(self):
        self.select = Select([])
    
    def test_reduced_defaults_to_false(self):
        self.assertEqual(self.select._reduced, False)
    
    def test_reduced_in_kwarg(self):
        select = Select([], reduced=True)
        self.assertEqual(select._reduced, True)
    
    def test_reduced_method(self):
        select = self.select.reduced()
        self.assertEqual(select._reduced, True)
        select = select.reduced(False)
        self.assertEqual(select._reduced, False)
    
    def test_method_is_generative(self):
        select = self.select.reduced()
        self.assert_(select is not self.select)
    
    def test_mutually_exclusive_with_distinct(self):
        self.assertRaises(ValueError, Select, [], distinct=True, reduced=True)
        select = Select([], distinct=True).reduced()
        self.assertEqual(select._distinct, False)

class TestOrderBy(unittest.TestCase):
    def setUp(self):
        self.select = Select([])
    
    def test_order_by_defaults_to_none(self):
        self.assertEqual(self.select._order_by, None)
    
    def test_order_by_method(self):
        a, b = Variable('a'), Variable('b')
        select = self.select.order_by(a)
        self.assertEqual(len(select._order_by), 1)
        self.assert_(a in select._order_by)
        select = self.select.order_by(a, b)
        self.assertEqual(len(select._order_by), 2)
        self.assert_(b in select._order_by)
    
    def test_method_is_generative(self):
        a = Variable('a')
        select = self.select.order_by(a)
        self.assert_(select is not self.select)


if __name__ == '__main__':
    unittest.main()
