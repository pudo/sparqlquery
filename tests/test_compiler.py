#!/usr/bin/env python
import re
import unittest
from rdflib import Variable, Namespace
from telescope.sparql.select import Select
from telescope.sparql.compiler import SelectCompiler

TEST = Namespace('http://www.example.com/test#')
a, b, c, x, y, z = map(Variable, 'abcxyz')

def normalize(text):
    return re.sub(r'\s+', ' ', unicode(text).strip())

class TestSelectCompiler(unittest.TestCase):
    def test_select_empty_graph_pattern_output(self):
        select = Select([a])
        compiler = SelectCompiler(select)
        self.assertCompileOutputs(compiler, 'SELECT ?a WHERE { }')
    
    def test_select_basic_graph_pattern_output(self):
        select = Select([a]).where((a, TEST.b, 'c'))
        compiler = SelectCompiler(select)
        self.assertCompileOutputs(compiler,
            'SELECT ?a WHERE { ?a <http://www.example.com/test#b> "c" }'
        )
        compiler = SelectCompiler(select.where((a, TEST.y, 'z')))
        self.assertCompileOutputs(compiler,
            """SELECT ?a WHERE {
            ?a <http://www.example.com/test#b> "c" .
            ?a <http://www.example.com/test#y> "z"
            }"""
        )

    def test_select_optional_graph_pattern_output(self):
        select = Select([a]).where((a, TEST.b, 'c'), optional=True)
        compiler = SelectCompiler(select)
        self.assertCompileOutputs(compiler,
            'SELECT ?a WHERE { OPTIONAL { ?a <http://www.example.com/test#b> "c" } }'
        )
        compiler = SelectCompiler(select.where(
            (x, TEST.y, z), (z, TEST.y, a), optional=True
        ))
        self.assertCompileOutputs(compiler,
            """SELECT ?a WHERE {
            OPTIONAL { ?a <http://www.example.com/test#b> "c" }
            OPTIONAL {
                ?x <http://www.example.com/test#y> ?z .
                ?z <http://www.example.com/test#y> ?a
            } }"""
        )

    def test_select_multiple_graph_patterns_output(self):
        select = Select([a, z], (a, TEST.b, 'c')).where((a, TEST.y, z), optional=True)
        compiler = SelectCompiler(select)
        self.assertCompileOutputs(compiler,
            """SELECT ?a ?z WHERE {
            ?a <http://www.example.com/test#b> "c" .
            OPTIONAL { ?a <http://www.example.com/test#y> ?z }
            }"""
        )
        compiler = SelectCompiler(select.where(
            (x, TEST.y, z), (b, TEST.x, 'y')
        ).where((z, TEST.b, 'a'), optional=True))
        self.assertCompileOutputs(compiler,
            """SELECT ?a ?z WHERE {
            ?a <http://www.example.com/test#b> "c" .
            OPTIONAL { ?a <http://www.example.com/test#y> ?z }
            ?x <http://www.example.com/test#y> ?z .
            ?b <http://www.example.com/test#x> "y" .
            OPTIONAL { ?z <http://www.example.com/test#b> "a" }
            }"""
        )
    
    def assertCompileOutputs(self, compiler, expected):
        output = compiler.compile()
        return self.assertEqual(normalize(output), normalize(expected))


if __name__ == '__main__':
    unittest.main()

