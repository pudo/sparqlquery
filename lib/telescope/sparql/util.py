from rdflib import Variable
from telescope.sparql.expressions import Expression

def to_variable(value):
    while isinstance(value, Expression):
        value = value.value
    if value and not isinstance(value, Variable):
        value = Variable(value)
    return value

def to_list(obj):
    if not isinstance(obj, basestring):
        try:
            return list(obj)
        except TypeError:
            pass
    return [obj]

