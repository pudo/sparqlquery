from rdflib import ConjunctiveGraph, Namespace
from telescope.properties import *
from telescope.mapper import *
from telescope.declarative import Subject

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
PTREC = Namespace('tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#')

class Patient(Subject):
    RDF_TYPE = PTREC.Patient
    ccfid = Property(PTREC.hasCCFID)
    ssn = Property(PTREC.hasSocialSecurityNumber)
    race = Label(PTREC.hasRace)
    sex = Label(PTREC.hasSex)
    
    def __repr__(self):
        return "Patient(%r)" % (self.ccfid,)

class TemporalData(Subject):
    RDF_TYPE = PTREC.TemporalData
    min = Property(PTREC.hasDateTimeMin)
    max = Property(PTREC.hasDateTimeMax)
    
    def __repr__(self):
        return "TemporalData(%r, %r)" % (self.min, self.max)

class Event(Subject):
    RDF_TYPE = PTREC.Event
    type = Term(RDF.type)
    
    def __repr__(self):
        return "Event(%r)" % (self.type,)

class PatientRecord(Subject):
    RDF_TYPE = PTREC.PatientRecord
    patient = Single(Patient)
    events = Collection(Event)
    
    def __repr__(self):
        return "PatientRecord(%r)" % (self.patient.ccfid,)

if __name__ == '__main__':
    from rdflib.Graph import Graph
    from rdflib.syntax.NamespaceManager import NamespaceManager
    from FuXi.Rete import ReteNetwork
    from FuXi.Rete.RuleStore import N3RuleStore
    from FuXi.Rete.Util import generateTokenSet
    
    graph = ConjunctiveGraph()
    graph.load('60611165.rdf')
    
    patients = list(query(Patient, graph))
    
    # Try invoking inference...
    closure_delta = Graph()
    rule_store = N3RuleStore()
    ns_manager = NamespaceManager(Graph(rule_store))
    rule_graph = Graph(rule_store, namespace_manager=ns_manager)
    network = ReteNetwork(rule_store, inferredTarget=closure_delta, nsMap=rule_store.nsMgr)
    
    ontology = ConjunctiveGraph()
    ontology.load('PatientRecord-DL.owl')
    
    network.setupDescriptionLogicProgramming(ontology)
    network.feedFactsToAdd(generateTokenSet(ontology))
    network.feedFactsToAdd(generateTokenSet(graph))
