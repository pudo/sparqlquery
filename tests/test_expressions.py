import operator
from nose.tools import assert_raises
from rdflib import Variable, Namespace, URIRef, Literal, BNode
from sparqlquery.sparql.expressions import *
from sparqlquery.sparql.helpers import XSD
import helpers

class TestCreatingExpression:
    def setup(self):
        self.one = Expression(1)
        self.neg_one = Expression(1, operator.neg)

    def test_first_arg_sets_value(self):
        assert self.one.value == 1
        assert self.neg_one.value == 1

    def test_default_operator_is_none(self):
        assert self.one.operator is None

    def test_second_arg_sets_operator(self):
        assert self.neg_one.operator is operator.neg

    def test_default_language_is_none(self):
        assert self.one.language is None
        assert self.neg_one.language is None

    def test_default_datatype_is_none(self):
        assert self.one.datatype is None
        assert self.neg_one.datatype is None

class TestCreatingBinaryExpression:
    def setup(self):
        self.expr = BinaryExpression(operator.add, 1, 2)

    def test_first_arg_sets_operator(self):
        assert self.expr.operator is operator.add

    def test_second_arg_sets_left(self):
        assert self.expr.left == 1

    def test_third_arg_sets_right(self):
        assert self.expr.right == 2

class TestPrintingExpression:
    def test_repr_args_print_with_repr(self):
        args = ('a', operator.pos)
        expr = Expression(*args)
        assert repr(expr) == "Expression(%r, %r)" % args

    def test_repr_no_op_omits_operator_arg(self):
        expr = Expression(1)
        assert repr(expr) == "Expression(1)"

    def test_repr_arg_calls_n3_method(self):
        for n3_type in (Variable, URIRef, Literal, BNode):
            value = n3_type('test')
            value_repr = value.n3()
            expr = Expression(value)
            assert repr(expr) == "Expression(%s)" % value_repr

class TestPrintingBinaryExpression:
    def test_repr_args_print_with_repr(self):
        args = (operator.add, 1, 2)
        expr = BinaryExpression(*args)
        assert repr(expr) == "BinaryExpression(%r, %r, %r)" % args

class TestPrintingConditionalExpression:
    def test_repr_args_print_with_repr(self):
        args = (operator.or_, [True, False])
        expr = ConditionalExpression(*args)
        assert repr(expr) == "ConditionalExpression(%r, %r)" % args

class TestCallingExpressionMethods:
    def setup(self):
        self.expr = Expression(1)

    def test_lang_method_sets_language(self):
        expr = self.expr._lang('en')
        assert expr.language == 'en'
    
    def test_lang_method_is_generative(self):
        expr = self.expr._lang('en')
        assert expr is not self.expr

    def test_type_method_sets_datatype(self):
        expr = self.expr._type(XSD.integer)
        assert expr.datatype == XSD.integer

    def test_type_method_is_generative(self):
        expr = self.expr._type(XSD.integer)
        assert expr is not self.expr
    
    def test_pow_operator_sets_datatype(self):
        expr = self.expr ** XSD.integer
        assert expr.datatype == XSD.integer

    def test_compile_method_returns_string(self):
        assert isinstance(self.expr.compile(), basestring)

class TestCallingConditionalHelpers:
    def test_and_helper_returns_and_conditional(self):
        args = (True, False)
        expr = and_(*args)
        assert isinstance(expr, ConditionalExpression)
        assert expr.operator is operator.and_
        assert args == tuple(expr.operands) 

    def test_or_helper_returns_or_conditional(self):
        args = (True, False)
        expr = or_(*args)
        assert isinstance(expr, ConditionalExpression)
        assert expr.operator is operator.or_
        assert args == tuple(expr.operands) 

class TestGeneratingNewExpression:
    def setup(self):
        self.x = Expression('x')
        self.y = Expression('y')
        self.z = Expression('z')

    def test_logical_op_returns_conditional_expression(self):
        for op in helpers.CONDITIONAL_OPERATORS:
            expr = op(self.x, self.y)
            assert isinstance(expr, ConditionalExpression)
    
    def test_comparison_returns_binary_expression(self):
        for op in helpers.BINARY_OPERATORS:
            expr = op(self.x, self.y)
            assert isinstance(expr, BinaryExpression)

class TestCreatingVariableExpression:
    def setup(self):
        self.v = VariableExpressionConstructor()
    
    def test_call_returns_variable_expression(self):
        foo = self.v('foo')
        self.assert_is_variable_expression(foo, 'foo')

    def test_getattr_returns_variable_expression(self):
        foo = self.v.foo
        self.assert_is_variable_expression(foo, 'foo')

    def test_getitem_returns_variable_expression(self):
        foo = self.v['foo']
        self.assert_is_variable_expression(foo, 'foo')
    
    def test_variable_name_must_be_a_string(self):
        assert_raises(TypeError, self.v, 1)
    
    def assert_is_variable_expression(self, obj, name):
        assert isinstance(obj, Expression)
        assert isinstance(obj.value, Variable)
        assert obj.value == Variable(name)
