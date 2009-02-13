from rdflib import Variable
from telescope.sparql.expressions import Expression

def defrag(uri):
    if '#' in uri:
        namespace, fragment = uri.split('#', 1)
        return ('%s#' % namespace, fragment)
    else:
        namespace, fragment = uri.rsplit('/', 1)
        return ('%s/' % namespace, fragment)

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
