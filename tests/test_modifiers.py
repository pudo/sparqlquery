from nose.tools import assert_raises
from sparqlquery import Variable
from sparqlquery.exceptions import *
from sparqlquery.sparql.queryforms import *

class TestAddingLimitModifier:
    def setup(self):
        self.select = Select([])
    
    def test_limit_defaults_to_none(self):
        assert self.select._limit == None
    
    def test_limit_in_kwarg(self):
        select = Select([], limit=5)
        assert select._limit == 5
    
    def test_limit_in_slice(self):
        select = self.select[:10]
        assert select._limit == 10
        select = select[10:50]
        assert select._limit == 40
    
    def test_limit_method(self):
        select = self.select.limit(10)
        assert select._limit == 10

    def test_method_is_generative(self):
        select = self.select.limit(10)
        assert select is not self.select

class TestAddingOffsetModifier:
    def setup(self):
        self.select = Select([])
    
    def test_offset_defaults_to_none(self):
        assert self.select._offset is None
    
    def test_offset_in_kwarg(self):
        select = Select([], offset=5)
        assert select._offset == 5
    
    def test_offset_in_slice(self):
        select = self.select[:10]
        assert select._offset is None
        select = select[10:50]
        assert select._offset == 10
    
    def test_offset_method(self):
        select = self.select.offset(10)
        assert select._offset == 10
    
    def test_method_is_generative(self):
        select = self.select.offset(10)
        assert select is not self.select

class TestAddingDistinctModifier:
    def setup(self):
        self.select = Select([])
    
    def test_distinct_defaults_to_false(self):
        assert self.select._distinct == False

    def test_distinct_in_kwarg(self):
        select = Select([], distinct=True)
        assert select._distinct == True
    
    def test_distinct_method(self):
        select = self.select.distinct()
        assert select._distinct == True
        select = select.distinct(False)
        assert select._distinct == False
    
    def test_method_is_generative(self):
        select = self.select.distinct()
        assert select is not self.select
    
    def test_mutually_exclusive_with_reduced(self):
        assert_raises(InvalidRequestError, Select, [], distinct=True, reduced=True)
        select = Select([], reduced=True).distinct()
        assert select._reduced == False

class TestAddingReducedModifier:
    def setup(self):
        self.select = Select([])
    
    def test_reduced_defaults_to_false(self):
        assert self.select._reduced == False
    
    def test_reduced_in_kwarg(self):
        select = Select([], reduced=True)
        assert select._reduced == True
    
    def test_reduced_method(self):
        select = self.select.reduced()
        assert select._reduced == True
        select = select.reduced(False)
        assert select._reduced == False
    
    def test_method_is_generative(self):
        select = self.select.reduced()
        assert select is not self.select
    
    def test_mutually_exclusive_with_distinct(self):
        assert_raises(InvalidRequestError, Select, [], distinct=True, reduced=True)
        select = Select([], distinct=True).reduced()
        assert select._distinct == False

class TestAddingOrderByModifier:
    def setup(self):
        self.select = Select([])
    
    def test_order_by_defaults_to_none(self):
        assert self.select._order_by == None
    
    def test_order_by_method(self):
        a, b = Variable('a'), Variable('b')
        select = self.select.order_by(a)
        assert len(select._order_by) == 1
        assert a in select._order_by
        select = self.select.order_by(a, b)
        assert len(select._order_by) == 2
        assert b in select._order_by
    
    def test_method_is_generative(self):
        a = Variable('a')
        select = self.select.order_by(a)
        assert select is not self.select
