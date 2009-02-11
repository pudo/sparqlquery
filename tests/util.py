import unittest
import os.path
from rdflib import ConjunctiveGraph

def resource(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)

def graph(*filenames):
    graph = ConjunctiveGraph()
    for filename in filenames:
        graph.load(resource(filename))
    return graph

class TestLoader(unittest.TestLoader):
    def loadTestsFromModule(self, module):
        tests = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                tests.append(self.loadTestsFromTestCase(obj))
            elif isinstance(obj, unittest.TestSuite):
                tests.append(obj)
        return self.suiteClass(tests)

