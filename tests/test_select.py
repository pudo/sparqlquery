from nose.tools import assert_raises
from sparqlquery import Variable, Namespace
from sparqlquery.sparql.patterns import *
from sparqlquery.sparql.queryforms import Select
from sparqlquery.sparql.expressions import *
from sparqlquery.sparql.helpers import *

FOAF = Namespace('http://xmlns.com/foaf/0.1/')

class TestCreatingSelect:
    def test_variables_arg_is_required(self):
        assert_raises(TypeError, Select)
    
    def test_variables_arg_is_sufficient(self):
        try:
            select = Select([v.x])
        except Exception:
            assert False

    def test_unknown_kwargs_raises_exception(self):
        assert_raises(TypeError, Select, [], foo='bar')

class TestProjectingVariables:
    def setup(self):
        self.select = Select([])

    def test_variables_arg_adds_variables(self):
        select = Select([Variable('foo')])
        assert Variable('foo') in select.projection
    
    def test_variables_can_be_expressions(self):
        select = self.select.project(v.foo)
        assert Variable('foo') in select.projection
    
    def test_variables_can_be_rdflib_variables(self):
        select = self.select.project(Variable('foo'))
        assert Variable('foo') in select.projection

    def test_variables_can_be_strings(self):
        select = self.select.project('foo')
        assert Variable('foo') in select.projection
    
    def test_method_is_generative(self):
        select = self.select.project(v.foo)
        assert select is not self.select
    
    def test_method_args_replace_projected_variables(self):
        select = self.select.project(v.foo, v.bar)
        assert Variable('foo') in select.projection
        assert Variable('bar') in select.projection
        select = self.select.project(v.baz)
        assert Variable('baz') in select.projection
        assert Variable('foo') not in select.projection
        assert Variable('bar') not in select.projection

class TestAddingWhereClauses:
    def setup(self):
        self.select = Select(['*'])
    
    def test_default_has_no_clauses(self):
        assert not self.select._where
    
    def test_patterns_arg_adds_clauses(self):
        select = Select([], [(v.x, FOAF.name, v.name)])
        for pattern in select._where.patterns:
            if isinstance(pattern, (Triple, GraphPattern)):
                break
        else:
            assert False
    
    def test_method_is_generative(self):
        select = self.select.where()
        assert select is not self.select
    
    def test_method_args_add_clauses(self):
        select = self.select.where(
            (v.x, FOAF.name, "Alice"), (v.x, FOAF.mbox, v.mbox)
        )
        assert len(select._where.patterns[-1].patterns) == 2
    
    def test_optional_kwarg_makes_optional_pattern(self):
        select = self.select.where((v.x, FOAF.mbox, v.mbox), optional=True)
        assert select._where.patterns[-1].optional

class TestAddingFilterConstraints:
    def setup(self):
        self.select = Select([])
    
    def test_method_is_generative(self):
        select = self.select.filter()
        assert select is not self.select

    def test_method_args_add_filters(self):
        select = self.select.filter(v.x > 1, v.name == "Alice")
        assert select._where.filters
