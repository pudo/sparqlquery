import operator
from rdflib import URIRef

__all__ = ['Expression', 'BinaryExpression', 'ConditionalExpression', 'and_', 'or_']

unary = lambda op: lambda self: Expression(self, op)
binary = lambda op: lambda self, other: BinaryExpression(op, self, other)
binary.r = lambda op: lambda self, other: BinaryExpression(op, other, self)
conditional = lambda op: lambda self, other: ConditionalExpression(op, (self, other))
conditional.r = lambda op: lambda self, other: ConditionalExpression(op, (other, self))

class Expression(object):
    def __init__(self, expression, operator=None, lang=None, type=None):
        self.expression = expression
        self.operator = operator
        self.language = lang
        self.datatype = type
    
    def __repr__(self):
        expression = self.expression
        if hasattr(expression, 'n3'):
            expression = expression.n3()
        if self.operator:
            return "Expression(%r, %r)" % (expression, self.operator)
        else:
            return "Expression(%r)" % (expression,)

    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.__dict__.update(kwargs)
        return clone
    
    def _lang(self, language):
        """Emulates @lang."""
        return self._clone(language=language)
    
    def _type(self, datatype):
        """Emulates ^^type."""
        return self._clone(datatype=datatype)
    
    # Special operators.
    
    def __pow__(self, datatype):
        """Emulates ^^type."""
        return self._type(datatype)
    
    # Logical operators.
    
    __or__ = conditional(operator.or_)
    __ror__ = conditional.r(operator.or_)
    __and__ = conditional(operator.and_)
    __rand__ = conditional.r(operator.and_)
    
    # Unary operators.
    
    __pos__ = unary(operator.pos)
    __neg__ = unary(operator.neg)
    __invert__ = unary(operator.invert)
    
    # Numeric operators.
    
    __eq__ = binary(operator.eq)
    __ne__ = binary(operator.ne)
    __lt__ = binary(operator.lt)
    __gt__ = binary(operator.gt)
    __le__ = binary(operator.le)
    __ge__ = binary(operator.ge)
    
    # Additive operators.
    
    __add__ = binary(operator.add)
    __radd__ = binary.r(operator.add)
    __sub__ = binary(operator.sub)
    
    # Multiplicative operators.
    
    __mul__ = binary(operator.mul)
    __rmul__ = binary.r(operator.mul)
    __div__ = binary(operator.div)
    __rdiv__ = binary.r(operator.div)

class BinaryExpression(Expression):
    def __init__(self, operator, left, right):
        Expression.__init__(self, None, operator)
        self.left = left
        self.right = right

class ConditionalExpression(Expression):
    def __init__(self, operator, expressions):
        Expression.__init__(self, None, operator)
        self.expressions = expressions

def or_(*expressions):
    return ConditionalExpression(operator.or_, expressions)

def and_(*expressions):
    return ConditionalExpression(operator.and_, expressions)

