from telescope import Variable

class Query(object):
    def __init__(self, class_, session=None):
        self.class_ = class_
        self.session = session
        self.select = class_._mapper.select
    
    def __iter__(self):
        return self.execute()
    
    def _clone(self, **kwargs):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.__dict__.update(kwargs)
        return clone
    
    def execute(self, graph=None):
        if graph is None:
            graph = self.session.graph
        manager = self.class_._manager
        mapper = self.class_._mapper
        variables = map(Variable, self.class_._manager.properties)
        triples = []
        for name, property in self.class_._manager:
            triples.extend(property.triples(mapper.identifier, Variable(name)))
        select = self.select.project(variables, append=True).where(*triples)
        results = select.execute(graph)
        return mapper.bind_results(graph, select, results)
    
    def filter(self, *constraints, **kwargs):
        manager = self.class_._manager
        mapper = self.class_._mapper
        triples = []
        for key, value in kwargs.iteritems():
            property = self.class_._manager[key]
            triples.extend(property.triples(self.class_))
        return self._clone(select=self.select.filter())
