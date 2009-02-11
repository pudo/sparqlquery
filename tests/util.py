import os.path
from rdflib import ConjunctiveGraph

def resource(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)

def graph(*filenames):
    graph = ConjunctiveGraph()
    for filename in filenames:
        graph.load(resource(filename))
    return graph

