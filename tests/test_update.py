from rdflib.namespace import DC
from rdflib import URIRef, Literal
from sparqlquery.sparql.query import SPARQLUpdateQuery
from sparqlquery.exceptions import InvalidRequestError
from sparqlquery import v
from nose.tools import raises


class TestUpdate(object):
    def test_insert_data(self):
        insert_data = (URIRef('http://example/book1'), DC.title, Literal('A new book')),\
                      (URIRef('http://example/book1'), DC.creator, Literal('A.N.Other'))
        q = SPARQLUpdateQuery().insert(insert_data)
        oracle_sparql = u"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
INSERT DATA
{
<http://example/book1> dc:title "A new book" .
<http://example/book1> dc:creator "A.N.Other"
}"""
        sparql = q.compile(prefix_map={DC: 'dc'})
        assert sparql == oracle_sparql

    def test_delete_data(self):
        delete_data = (URIRef('http://example/book1'), DC.title, Literal('A new book')),\
                       (URIRef('http://example/book1'), DC.creator, Literal('A.N.Other'))
        q = SPARQLUpdateQuery().delete(delete_data)
        oracle_sparql = u"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
DELETE DATA
{
<http://example/book1> dc:title "A new book" .
<http://example/book1> dc:creator "A.N.Other"
}"""
        sparql = q.compile(prefix_map={DC: 'dc'})
        assert sparql == oracle_sparql

    @raises(InvalidRequestError)
    def test_empty_query_raises(self):
        SPARQLUpdateQuery().compile()

    def test_delete_where(self):
        where = (v.x, DC.creator, Literal('John Doe')),\
                 (v.x, DC.price, v.price)
        q = SPARQLUpdateQuery(where).filter(v.price <= 20).delete()
        oracle_sparql = u"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
DELETE WHERE
{
?x dc:creator "John Doe" .
?x dc:price ?price .
FILTER (?price <= 20)
}"""
        sparql = q.compile(prefix_map={DC: 'dc'})
        assert sparql == oracle_sparql

    def test_insert_where(self):
        where = (v.x, DC.creator, Literal('John Doe')), \
                (v.x, DC.price, v.price)
        insert = [(v.x, DC.title, Literal('My short life'))]
        q = SPARQLUpdateQuery(where).filter(v.price <= 20).insert(insert)
        oracle_sparql = u"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
INSERT
{
?x dc:title "My short life"
}
WHERE
{
?x dc:creator "John Doe" .
?x dc:price ?price .
FILTER (?price <= 20)
}"""
        sparql = q.compile(prefix_map={DC: 'dc'})
        assert sparql == oracle_sparql

    def test_delete_insert_where(self):
        where = (v.x, DC.creator, Literal('John Doe')), \
                (v.x, DC.price, v.price)
        delete = [(v.x, DC.title, 'My long and happy life')]
        insert = [(v.x, DC.title, Literal('My short life'))]
        q = SPARQLUpdateQuery(where).filter(v.price <= 20).delete(delete).insert(insert)
        oracle_sparql = u"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
DELETE
{
?x dc:title "My long and happy life"
}
INSERT
{
?x dc:title "My short life"
}
WHERE
{
?x dc:creator "John Doe" .
?x dc:price ?price .
FILTER (?price <= 20)
}"""
        sparql = q.compile(prefix_map={DC: 'dc'})
        assert sparql == oracle_sparql
