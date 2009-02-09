from operator import or_, and_, pos, neg, invert, eq, ne, lt, gt, le, ge, add, sub, mul, div
from telescope.sparql.expressions import Expression, BinaryExpression

class Operator(object):
    def __init__(self, operator):
        self.operator = operator
    
    def __call__(self, *args):
        return FunctionCall(self.operator, args)
    
    def __repr__(self):
        return "Operator(%r)" % (self.operator,)

class BinaryOperator(Operator):
    def __call__(self, left, right):
        return BinaryExpression(self.operator, left, right)

class FunctionCall(Expression):
    def __init__(self, operator, arg_list):
        Expression.__init__(self, None, operator)
        self.arg_list = arg_list
    
    def __repr__(self):
        return "FunctionCall(%r, %r)" % (self.operator, self.arg_list)

def asc(variable):
    return BuiltinOperator(asc, (variable,))

def desc(variable):
    return BuiltinOperator(desc, (variable,))

class OperatorConstructor(object):
    def __init__(self, namespace=None):
        self._namespace = namespace
    
    def __getattribute__(self, name):
        if name.startswith('_') or self._namespace is None:
            return object.__getattribute__(self, name)
        else:
            return Operator(self._namespace[name])
    
    def __getitem__(self, name):
        return getattr(self, name.replace('-', '_'))
    
    def __call__(self, namespace):
        return self.__class__(namespace)
    
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
        return BinaryOperator('logical-or')(left, right)
    
    def logical_and(self, left, right):
        return BinaryOperator('logical-and')(left, right)
    
    def RDFTerm_equal(self, term1, term2):
        return BinaryOperator('RDFTerm-equal')(term2, term2)
    
    def sameTerm(self, term1, term2):
        return Operator('sameTerm')(term1, term2)
    
    def langMatches(self, tag, range):
        return Operator('langMatches')(tag, range)
    
    def regex(self, text, pattern, flags=None):
        params = [text, pattern] + (flags and [flags] or [])
        return Operator('regex')(*params)

op = OperatorConstructor()
