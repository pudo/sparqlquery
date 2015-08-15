from sparqlquery import Namespace, Variable, URIRef
from sparqlquery.sparql.expressions import Expression
from sparqlquery.sparql.operators import *
from sparqlquery.sparql.helpers import *
import helpers

FUNC = Namespace('http://example.org/func#')

class TestCreatingOperator:
    def setup(self):
        self.operator = Operator('test')

    def test_first_arg_sets_operator(self):
        assert self.operator.operator == 'test'

class TestCallingOperator:
    def setup(self):
        self.operator = Operator('test')

    def test_operator_is_callable(self):
        assert callable(self.operator)

    def test_operator_call_accepts_any_args(self):
        try:
            self.operator()
        except TypeError:
            assert False
        try:
            self.operator('a', 2, v.c, 4.0)
        except TypeError:
            assert False

class TestPrintingOperator:
    def test_repr_arg_prints_with_repr(self):
        operator = Operator('test')
        repr_arg = repr('test')
        assert repr(operator) == "Operator(%s)" % repr_arg

class TestPrintingFunctionCall:
    def test_repr_args_print_with_repr(self):
        operator = Operator('test')
        args = (operator, ['a'])
        func_call = FunctionCall(*args)
        assert repr(func_call) == "FunctionCall(%r, %r)" % args

class TestCreatingCustomOperatorConstructor:
    def test_first_arg_sets_namespace(self):
        func = OperatorConstructor(FUNC)
        assert func._namespace == FUNC

    def test_calling_builtin_op_creates_custom(self):
        op = BuiltinOperatorConstructor()
        func = op(FUNC)
        assert isinstance(func, OperatorConstructor)
        assert func._namespace == FUNC

class TestCallingCustomOperators:
    FUNC_OPERATOR_FIXTURES = ['foo', 'bar', 'baz']
    
    def setup(self):
        self.func = OperatorConstructor(FUNC)

    def test_getattr_gets_operator(self):
        for op in self.FUNC_OPERATOR_FIXTURES:
            operator = getattr(self.func, op)
            assert isinstance(operator, Operator)

    def test_getitem_gets_operator(self):
        for op in self.FUNC_OPERATOR_FIXTURES:
            operator = self.func[op]
            assert isinstance(operator, Operator)

class TestCallingBuiltinOperators:
    ARG_LIST_FIXTURES = {
        'bound': [Variable('x')],
        'isIRI': [URIRef('mailto:bob@example.org')],
        'isBlank': [Variable('x')],
        'isLiteral': ["test"],
        'str': [URIRef('mailto:bob@example.org')],
        'lang': ["test"],
        'datatype': ["test"],
        'logical-or': [True, False],
        'logical-and': [True, False],
        'RDFTerm-equal': [Variable('x'), Variable('a')],
        'sameTerm': [Variable('x'), Variable('x')],
        'langMatches': ['en', 'FR'],
        'regex': [Variable('x'), "^bob", 'i']
    }

    def setup(self):
        self.op = BuiltinOperatorConstructor()

    def test_getattr_gets_callable(self):
        for op in helpers.BUILTIN_OPERATORS:
            operator = getattr(self.op, op.replace('-', '_'), None)
            assert callable(operator)

    def test_getitem_gets_callable(self):
        for op in helpers.BUILTIN_OPERATORS:
            operator = self.op[op]
            assert callable(operator)
    
    def test_operator_returns_expression(self):
        for op, arg_list in self.ARG_LIST_FIXTURES.iteritems():
            operator = self.op[op]
            value = operator(*arg_list)
            assert isinstance(value, Expression)

