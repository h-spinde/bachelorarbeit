##REALLY ONLY CALLS ON ALL OTHER FILES IN ORDER

import ontology_extraction
import compare

def start_interaction(nmbr, letter):

    x= "sfo" #input("Enter Ontology Acronym: ") TODO: Change back
    ontology_name = "../../../ontologies/" + x + "/" + x + ".owx"
    ontology_extraction.init(ontology_name)

    check_all = bool(True) #input("Check all entities? (y/n) ").lower().startswith('y')
    if check_all:
       compare.check_all(nmbr, letter)
    else:
       clssid: str = "http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#" + input("Enter IRI: ") #TODO: Change back
       compare.check_entity(clssid, nmbr, letter)

#for i in range(14,20):
#    start_interaction(i, "a")
#    start_interaction(i, "b")
#    start_interaction(i, "c")
start_interaction(20, "a")
start_interaction(20, "b")
start_interaction(20, "c")


#TODO Add: Make List of non-matching (eval will help)
