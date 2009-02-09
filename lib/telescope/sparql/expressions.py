from rdflib import URIRef

class Expression(object):
    def __init__(self, expression, operator=None, lang=None, type=None):
        self.expression = expression
        self.operator = operator
        self.language = lang
        self.datatype = type
    
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
    
    def __or__(self, other):
        return BinaryExpression(operator.or_, self, other)
    
    def __and__(self, other):
        return BinaryExpression(operator.and_, self, other)
    
    # Unary operators.
    
    def __pos__(self):
        return Expression(operator.pos, self)
    
    def __neg__(self):
        return Expression(operator.neg, self)
    
    def __invert__(self):
        return Expression(operator.invert, self)
    
    # Numeric operators.
    
    def __eq__(self, other):
        return BinaryExpression(operator.eq, self, other)
    
    def __ne__(self, other):
        return BinaryExpression(operator.ne, self, other)
    
    def __lt__(self, other):
        return BinaryExpression(operator.lt, self, other)
    
    def __gt__(self, other):
        return BinaryExpression(operator.gt, self, other)
    
    def __le__(self, other):
        return BinaryExpression(operator.le, self, other)
    
    def __ge__(self, other):
        return BinaryExpression(operator.ge, self, other)
    
    # Additive operators.
    
    def __add__(self, other):
        return BinaryExpression(operator.add, self, other)
    
    def __sub__(self, other):
        return BinaryExpression(operator.sub, self, other)
    
    # Multiplicative operators.
    
    def __mul__(self, other):
        return BinaryExpression(operator.mul, self, other)
    
    def __div__(self, other):
        return BinaryExpression(operator.div, self, other)

class BinaryExpression(Expression):
    def __init__(self, operator, left, right):
        Expression.__init__(self, operator, None)
        self.left = left
        self.right = right

def lang(expression, language):
    return Expression(expression, lang=language)

def datatype(expression, type):
    return Expression(expression, type=type)
