from telescope.sparql.expressions import Expression

class Operator(Expression):
    def __init__(self, iri, params):
        Expression.__init__(self, iri, None)
        self.params = tuple(params)
    
    def __call__(self, *args):
        return self.__class__(self.iri, args)

class BuiltinOperator(Operator):
    def __init__(self, name, params):
        Operator.__init__(self, None, params)
        Expression.__init__(self, name, None)
        self.operator = name
    
    def __call__(self, *args):
        return self.__class__(self.name, args)

class OperatorConstructor(object):
    def __init__(self, namespace=None):
        self._namespace = namespace
    
    def __getattribute__(self, name):
        if name.startswith('_') or self._namespace is None:
            return object.__getattribute__(self, name)
        else:
            return Operator(self._namespace[name])
    
    def __call__(self, namespace):
        return self.__class__(namespace)
    
    def bound(self, variable):
        return BuiltinOperator('bound', [variable])
    
    def isIRI(self, term):
        return BuiltinOperator('isIRI', [term])
    
    def isBlank(self, term):
        return BuiltinOperator('isBlank', [term])
    
    def isLiteral(self, term):
        return BuiltinOperator('isLiteral', [term])
    
    def str(self, expression):
        return BuiltinOperator('str', [expression])
    
    def lang(self, literal):
        return BuiltinOperator('lang', [literal])
    
    def datatype(self, literal):
        return BuiltinOperator('datatype', [literal])
    
    def sameTerm(self, term1, term2):
        return BuiltinOperator('sameTerm', [term1, term2])
    
    def langMatches(self, tag, range):
        return BuiltinOperator('langMatches', [tag, range])
    
    def regex(self, text, pattern, flags=None):
        params = [text, pattern] + (flags and [flags] or [])
        return BuiltinOperator('regex', params)

op = OperatorConstructor()
