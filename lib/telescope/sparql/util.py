from rdflib import Variable
from telescope.sparql.expressions import Expression

def defrag(uri):
    if '#' in uri:
        namespace, fragment = uri.split('#', 1)
        return ('%s#' % namespace, fragment)
    else:
        namespace, fragment = uri.rsplit('/', 1)
        return ('%s/' % namespace, fragment)

def to_variable(obj):
    while isinstance(obj, Expression):
        obj = obj.value
    if isinstance(obj, Variable):
        return obj
    elif isinstance(obj, basestring):
        if obj:
            return Variable(obj)
        else:
            raise ValueError("Empty variable name.")
    else:
        raise TypeError("Variable names must be strings.")

def to_list(obj):
    if not isinstance(obj, basestring):
        try:
            return list(obj)
        except TypeError:
            pass
    return [obj]
