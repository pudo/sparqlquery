import operator
from rdflib import Variable

__all__ = ['Expression', 'BinaryExpression', 'ConditionalExpression',
           'VariableExpressionConstructor', 'and_', 'or_']

unary = lambda op: lambda self: Expression(self, op)
binary = lambda op: lambda self, other: BinaryExpression(op, self, other)
binary.r = lambda op: lambda self, other: BinaryExpression(op, other, self)
conditional = lambda op: lambda self, other: ConditionalExpression(op, (self, other))
conditional.r = lambda op: lambda self, other: ConditionalExpression(op, (other, self))

class Expression(object):
    def __init__(self, value, operator=None, lang=None, type=None):
        self.value = value
        self.operator = operator
        self.language = lang
        self.datatype = type
    
    def __repr__(self):
        value = self.value
        if hasattr(value, 'n3'):
            value = value.n3()
        if self.operator:
            return "Expression(%r, %r)" % (value, self.operator)
        else:
            return "Expression(%r)" % (value,)

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
    
    def compile(self, prefix_map=None):
        from telescope.sparql.compiler import ExpressionCompiler
        return ExpressionCompiler(prefix_map).compile(self)

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

    def __repr__(self):
        return "BinaryExpression(%r, %r, %r)" % (self.operator, self.left, self.right)

class ConditionalExpression(Expression):
    def __init__(self, operator, operands):
        Expression.__init__(self, None, operator)
        self.operands = operands

    def __repr__(self):
        return "ConditionalExpression(%r, %r)" % (self.operator, self.operands)

def and_(*operands):
    return ConditionalExpression(operator.and_, operands)

def or_(*operands):
    return ConditionalExpression(operator.or_, operands)

class VariableExpressionConstructor(object):
    def __call__(self, name):
        return Expression(Variable(name))

    def __getattr__(self, name):
        return self(name)

    def __getitem__(self, name):
        return self(name)

