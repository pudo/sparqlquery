import os
from datetime import datetime, timedelta
try:
    from rdflib import ConjunctiveGraph, Namespace, Variable
except ImportError:
    from rdflib.graph import ConjunctiveGraph
    from rdflib.term import Namespace, Variable
from telescope import *
from telescope.sparql.helpers import subject
from telescope.properties import *
from telescope.mapper import *
from telescope.declarative import Subject

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
PTREC = Namespace('tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#')
DNODE = Namespace('http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#')

PREFIX_MAP = {PTREC: 'ptrec', DNODE: 'dnode'}
   
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

graph = ConjunctiveGraph()

def get_index_event(cohort_line, graph=graph):
    """
    Splits `cohort_line`, a string formatted like "<ccfid> <YYYY-mm-dd> <n>",
    into the CCFID and operation event identifier, and returns the result of
    querying `graph` for that operation.

    The patient record graph will be loaded into `graph`, and must be an
    RDF/XML file named "<ccfid>.rdf" in the directory specified by the
    environment variable `RDF_DIRECTORY`.

    For example, "12345678 2009-01-01 2" will load "12345678.rdf" into `graph`
    and find that patient's second operation event on January 1, 2009.

    """
    # Determine the query parameters.
    ccfid, surg_date, surg_seq = cohort_line.split()
    surg_min = datetime.strptime(surg_date, '%Y-%m-%d')
    surg_max = surg_min + timedelta(days=1)
    index = int(surg_seq) - 1

    # Load the patient record.
    rdf_dir = os.environ['RDF_DIRECTORY']
    rdf_file = os.path.join(rdf_dir, '%s.rdf' % ccfid)
    graph.load(rdf_file, publicID=ccfid)

    # Construct the query.
    query = Select([v.event, v.start_min, v.start_max]).where(
        v.record[is_a: PTREC.PatientRecord,
                 DNODE.contains: v.patient,
                 DNODE.contains: v.event],
        v.patient[is_a: PTREC.Patient,
                  PTREC.hasCCFID: Literal(ccfid, datatype=XSD.string)],
        v.event[is_a: PTREC.Event_management_operation,
                DNODE.contains: v.start],
        v.start[is_a: PTREC.EventStartDate,
                PTREC.hasDateTimeMin: v.start_min,
                PTREC.hasDateTimeMax: v.start_max]
    ).filter(
        v.start_min >= surg_min, v.start_max < surg_max
    ).order_by(v.start_min).limit(1).offset(index)
    
    # Return the query results.
    return query.execute(graph, PREFIX_MAP)

