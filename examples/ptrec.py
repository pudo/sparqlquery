from rdflib import ConjunctiveGraph, Namespace, Variable
from rdflib.Graph import Graph
from telescope.properties import *
from telescope.mapper import *
from telescope.declarative import Subject

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
PTREC = Namespace('tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#')
DNODE = Namespace('http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#')

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

