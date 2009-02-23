import os.path
import operator
from telescope import ConjunctiveGraph

UNARY_OPERATORS = [operator.pos, operator.neg, operator.invert, operator.inv]
CONDITIONAL_OPERATORS = [operator.and_, operator.or_]
BINARY_OPERATORS = [operator.eq, operator.ne, operator.lt, operator.gt,
                    operator.le, operator.ge, operator.add, operator.sub,
                    operator.mul, operator.div]
BUILTIN_OPERATORS = ['bound', 'isIRI', 'isBlank', 'isLiteral', 'str',
                     'lang', 'datatype', 'logical-or', 'logical-and',
                     'RDFTerm-equal', 'sameTerm', 'langMatches', 'regex']

def resource(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)

def graph(*filenames):
    graph = ConjunctiveGraph()
    for filename in filenames:
        graph.load(resource(filename))
    return graph
