import os
from datetime import datetime, timedelta
from rdflib import ConjunctiveGraph, Namespace, Variable
from rdflib.Graph import Graph
from telescope import *
from telescope.sparql.helpers import subject
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

def get_index_event(cohort_line):
    ccfid, surg_date, surg_seq = cohort_line.split()
    rdf_dir = os.environ['RDF_DIRECTORY']
    rdf_file = os.path.join(rdf_dir, '%s.rdf' % ccfid)
    graph = ConjunctiveGraph()
    graph.load(rdf_file)
    surg_min = datetime.strptime(surg_date, '%Y-%m-%d')
    surg_max = surg_min + timedelta(days=1)
    offset = int(surg_seq) - 1

    query = Select([v.event, v.start_min, v.start_max]).where(
        v.event[is_a: PTREC.Event_management_operation,
                DNODE.contains: v.start],
        v.start[is_a: PTREC.EventStartDate,
                PTREC.hasDateTimeMin: v.start_min,
                PTREC.hasDateTimeMax: v.start_max]
    ).filter(
        v.start_min >= surg_min, v.start_max < surg_max
    ).order_by(v.start_min).limit(1).offset(offset)

    prefix_map = {PTREC: 'ptrec', DNODE: 'dnode'}
    return query.execute(graph, prefix_map)
