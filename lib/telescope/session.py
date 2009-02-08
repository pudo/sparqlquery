class Session(object):
    def __init__(self, graph=None):
        self.identity_map = {}
        self.graph = graph
    
    def query(self, class_, graph=None):
        if graph is None:
            graph = self.graph
        return class_._mapper.query(graph, self)
