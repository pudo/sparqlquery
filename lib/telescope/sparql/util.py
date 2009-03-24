try:
    from rdflib import Variable
except ImportError:
    from rdflib.term import Variable
from telescope.sparql.expressions import Expression

def defrag(uri, prefix_map=None):
    if prefix_map is None:
        if '#' in uri:
            namespace, fragment = uri.split('#', 1)
            return ('%s#' % namespace, fragment)
        elif '/' in uri:
            namespace, fragment = uri.rsplit('/', 1)
            return ('%s/' % namespace, fragment)
    else:
        for prefix, namespace in prefix_map.iteritems():
            if uri.startswith(namespace):
                return (prefix, uri[len(namespace):])
    return (None, uri)

def to_qname(uri, prefix_map):
    prefix, name = defrag(uri, prefix_map)
    if prefix is not None:
        return '%s:%s' % (prefix, name)
    else:
        return name

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
