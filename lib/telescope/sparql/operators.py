from operator import or_, and_, pos, neg, inv, invert
from operator import eq, ne, lt, gt, le, ge, add, sub, mul, div
from telescope.sparql.expressions import Expression, BinaryExpression

__all__ = ['Operator', 'FunctionCall', 'OperatorConstructor',
           'BuiltinOperatorConstructor']

not_ = invert

class Operator(object):
    def __init__(self, operator):
        self.operator = operator
    
    def __call__(self, *args):
        return FunctionCall(self.operator, args)
    
    def __repr__(self):
        return "Operator(%r)" % (self.operator,)

class FunctionCall(Expression):
    def __init__(self, operator, arg_list):
        super(FunctionCall, self).__init__(None, operator)
        self.arg_list = arg_list
    
    def __repr__(self):
        return "FunctionCall(%r, %r)" % (self.operator, self.arg_list)

class OperatorConstructor(object):
    def __init__(self, namespace):
        self._namespace = namespace
    
    def __getattribute__(self, operator):
        try:
            value = super(OperatorConstructor, self).__getattribute__(operator)
        except AttributeError:
            if self._namespace:
                operator = self._namespace[operator]
            value = Operator(operator)
        return value
    
    def __getitem__(self, operator):
        return getattr(self, operator.replace('-', '_'))

class BuiltinOperatorConstructor(OperatorConstructor):
    def __init__(self):
        super(BuiltinOperatorConstructor, self).__init__(None)

    def __call__(self, namespace):
        return OperatorConstructor(namespace)

    def bound(self, variable):
        return Operator('bound')(variable)
    
    def isIRI(self, term):
        return Operator('isIRI')(term)
    
    def isBlank(self, term):
        return Operator('isBlank')(term)
    
    def isLiteral(self, term):
        return Operator('isLiteral')(term)
    
    def str(self, expression):
        return Operator('str')(expression)
    
    def lang(self, literal):
        return Operator('lang')(literal)
    
    def datatype(self, literal):
        return Operator('datatype')(literal)
    
    def logical_or(self, left, right):
        return BinaryExpression(or_, left, right)
    
    def logical_and(self, left, right):
        return BinaryExpression(and_, left, right)
    
    def RDFTerm_equal(self, left, right):
        return BinaryExpression(eq, left, right)
    
    def sameTerm(self, left, right):
        return Operator('sameTerm')(left, right)
    
    def langMatches(self, tag, range):
        return Operator('langMatches')(tag, range)
    
    def regex(self, text, pattern, flags=None):
        params = [text, pattern] + (flags and [flags] or [])
        return Operator('regex')(*params)

