from rdflib import ConjunctiveGraph, Namespace, Variable
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


if __name__ == '__main__':
    from rdflib.Graph import Graph
    from rdflib.syntax.NamespaceManager import NamespaceManager
    from FuXi.Rete import ReteNetwork
    from FuXi.Rete.RuleStore import N3RuleStore
    from FuXi.Rete.Magic import MagicSetTransformation
    from FuXi.Rete.Util import generateTokenSet
    from FuXi.Syntax.InfixOWL import *
    from FuXi.DLP import SKOLEMIZED_CLASS_NS
    
    graph = Graph()
    graph.parse('/Users/exogen/Desktop/60611165.rdf')
    # graph.parse('PatientRecord-DL.owl')
    
    patients = list(query(Patient, graph))
    
    # Try invoking inference...
    closure_delta = Graph()
    rule_store = N3RuleStore()
    ns_manager = NamespaceManager(Graph(rule_store))
    rule_graph = Graph(rule_store, namespace_manager=ns_manager)
    network = ReteNetwork(rule_store, inferredTarget=closure_delta, nsMap=rule_store.nsMgr)
    
    ontology = Graph()
    ontology.parse('/Users/exogen/Desktop/PatientRecord-DL.owl')
    
    ontoogy2 = Graph()
    # Namespace bindings
    namespace_manager = NamespaceManager(ontology2)
    namespace_manager.bind(u'skolem', SKOLEMIZED_CLASS_NS)
    namespace_manager.bind(u'ptrec', PTREC)
    namespace_manager.bind(u'dnode', DNODE)
    namespace_manager.bind(u'skolem', SKOLEMIZED_CLASS_NS)
    ontology2.namespace_manager = namespace_manager
    for prefix, uri in ontology2.namespaces():
        if prefix:
            rule_store.bind(prefix, uri)
    
    # The next line fails with:
    # AssertionError: Cannot conclude existensial set membershipHFgNRrRw3255
    # network.setupDescriptionLogicProgramming(ontology)
    # network.feedFactsToAdd(generateTokenSet(ontology))
    # network.feedFactsToAdd(generateTokenSet(graph))
    _PTREC = ClassNamespaceFactory(PTREC)
    Individual.factoryGraph = ontology
    
    # The serialize method will copy over the RDF statements for
    # the given Class object into the user-specified graph
    # In this way we can 'graft' OWL-DL class descriptions
    # from the larger, source graph
    _PTREC.Patient.serialize(ontology2)
    _PTREC.Event.serialize(ontology2)
    _PTREC.TemporalData.serialize(ontology2)
    
    # sip-optimal OWL SPARQL BGP entailment (rule compression):
    # - one or more queries / goals (SPARQL Triple patterns)
    # - a logic program compiled from OWL / RDF facts
    # - a collection of sip graphs
    # - a list of derived predicates over the RDF fac graph
    
    # Known derived predicates.
    derivedPreds=[event.identifier,_PTREC.TemporalData.identifier]
    
    # Goals we are deriving via the descriptions in the OWL RDF.
    goals = [event.extentQuery, _PTREC.TemporalData.extentQuery]
    
    # All Events in SemanticDB repositories are 3-level taxonomies.  The lowest
    # levels are used exclusively in persistence.  The other two are
    # generalisations that can be inferred (i.e. derived predicates).
    
    # For ex: 3) ptrec:Event, 2) ptrec:Event_management 1) ptrec:Event_management_operation
    # subSumpteeIds returns an iterator over the OWL classes that 'subsume' the
    # user-specified class.
    # The Event taxonomy is 'grafted' over.
    for cl in event.subSumpteeIds():
        derivedPreds.append(cl)
        cl = Class(cl)
        cl.serialize(ontology2)
        for cl2 in cl.subSumpteeIds():
            derivedPreds.append(cl2)
            Class(cl2).serialize(ontology2)
    
    # Do the same with TemporalData.
    for cl in _PTREC.TemporalData.subSumpteeIds():
        cl = Class(cl)
        cl.serialize(ontology2)
    
    # Trigger sip-optimal OWL-DLP construction.
    rules = [rule for rule in
                network.setupDescriptionLogicProgramming(
                    ontology2,
                    addPDSemantics=False,
                    derivedPreds=derivedPreds,
                    constructNetwork=False)]
    
    print "Original program (%s clauses)" % (len(list(rules)))
    progLen=len(list(rules))
    magicRuleNo = 0
    for rule in MagicSetTransformation(None,
                                       rules,
                                       goals,
                                       derivedPreds=derivedPreds):
        print "\t",rule
        magicRuleNo+=1
        network.buildNetworkFromClause(rule)

    print "rate of reduction in the size of the program: ", (100-(float(magicRuleNo)/float(progLen))*100), magicRuleNo

    network.feedFactsToAdd(generateTokenSet(graph))

    #Show inferences made
    tNodeOrder = [tNode for tNode in network.terminalNodes
                            if network.instanciations.get(tNode,0)]
    for termNode in tNodeOrder:
        print termNode
        #print "\t %s => %s"%(lhsF,rhsF)
        print "\t", termNode.clause
        print "\t\t%s instanciations"%network.instanciations[termNode]

    #Now bind to all members of ptrec:Event as determined by entailed RDF graph
    entailedGraph = network.closureGraph(graph,store=graph.store)
    for node in event._get_extent(entailedGraph):
        for place,begin in entailedGraph.query(
            "SELECT ?PLACE ?DATE { ?evt dnode:contains [ ptrec:hasDateTimeMin ?DATE ]; ptrec:hasEventPlace ?PLACE  }",
            initNs=rule_store.nsMgr,
            initBindings={Variable('evt'):node}):
            print place,begin
