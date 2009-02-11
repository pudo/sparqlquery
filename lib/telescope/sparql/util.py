from rdflib import Variable
from telescope.sparql.expressions import Expression

class VariableExpressionConstructor(object):
    def __getattr__(self, name):
        return Expression(Variable(name))

    def __getitem__(self, name):
        return Expression(Variable(name))

v = VariableExpressionConstructor()

def to_variable(expression):
    while isinstance(expression, Expression):
        expression = expression.expression
    if expression and not isinstance(expression, Variable):
        expression = Variable(expression)
    return expression

def to_list(obj):
    if not isinstance(obj, basestring):
        try:
            return list(obj)
        except TypeError:
            pass
    return [obj]
