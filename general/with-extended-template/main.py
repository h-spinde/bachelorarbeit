##REALLY ONLY CALLS ON ALL OTHER FILES IN ORDER

import ontology_extraction
import compare
import print_positives

def start_interaction():

    x= input("Enter Ontology Acronym: ")
    ontology_name = "../ontologies/" + x + "/" + x + ".owx"
    ontology_extraction.init(ontology_name)

    check_all = input("Check all entities? (y/n) ").lower().startswith('y')
    if check_all:
       compare.check_all()
    else:
       clssid: str = input("Enter IRI: ")
       compare.check_entity(clssid)

start_interaction()
positives = print_positives.read_extended("results.json")

to_file = ""

print("\nFor the following entities, natural language definition and equiavalence axioms do not match:\n")
for entity in positives:
    print(entity)
    to_file += entity + ", \n"
    
print("\n")

make_file = input("Do you want to create a file listing these entities? (y/n) ").lower().startswith('y')
if make_file:
       to_file = to_file[:-4]
       with open("classes_to_review.txt", 'w') as file:
       # Write content to the file
           file.write(to_file)
