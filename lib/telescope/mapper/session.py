from telescope.mapper.query import Query

class Session(object):
    def __init__(self, graph=None):
        self.identity_map = {}
        self.graph = graph
    
    def query(self, class_):
        return Query(class_, self)
