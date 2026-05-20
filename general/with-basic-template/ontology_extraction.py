##Imports

import re

import pyhornedowl
from pyhornedowl.model import *
from pyhornedowl import PyIndexedOntology

import random
import string

import config

entities_in_sem = []
spaces = 4
global oe_onto

def init(ontology_name):
    global oe_onto
    oe_onto = pyhornedowl.open_ontology(ontology_name)

def get_all_classes():
    return oe_onto.get_classes()

def replace_label(entity, nonsense_label, query):
    query = re.sub(get_label(entity), nonsense_label, query, flags=re.IGNORECASE)
    query = re.sub(get_label(entity)+"s", nonsense_label+"s", query, flags=re.IGNORECASE)
    
    return query
    
def generate_queries(clssid):

   entities_in_sem.clear()
   
   #get basic query
   axioms_found, nl_def_found, semantic_def_found, basic_query = generate_basic_query(clssid)
   
   #replace labels with nonsense strings
   #attention! "tree" and "Tree" will be considered the same word, as will "tree" and "trees", so replacing one will also replace all instances of the other    
   for entity in entities_in_sem:
       if get_label(entity) == "owl:Thing":
           continue
       nonsense_label = ''.join(random.choice(string.ascii_letters) for x in range(7))
       basic_query = replace_label(entity, nonsense_label, basic_query)

   return axioms_found, nl_def_found, semantic_def_found, basic_query
   
   
def get_details_object_property(clss):
   entityaxioms = oe_onto.get_axioms_for_iri(clss)
   object_info = ""
   for axiom in entityaxioms:
       match type(axiom.component).__name__:
           case "DeclareOjectProperty":
               pass
           case "EquivalentObjectProperties":
               #equivalence_content = get_equivalence_relation(clss,axiom)
               #object_info += equivalence_content
               object_info += get_equivalence_relation(clss,axiom)
               #if not equivalence_content:
               #    pass
               #else:
               #    object_info += equivalence_content
           case "SubObjectPropertyOf":
               if str(axiom.component.sub) == clss:
                   object_info += "\n" + " "*spaces + "SubObjectPropertyOf" + class_or_axiom(axiom.component.sup, 1, 2)
           case "DisjointObjectProperties":
               object_info += "\n" + " "*spaces + "Is Disjoint With:"
               for expression in axiom.component.first:
                   if str(expression) == clss:
                       pass
                   else:
                       object_info += "\n" + " "*spaces*2 + class_or_axiom(expression, 0, 2)
           case "ObjectPropertyRange":
               #print("________________________ RANGE!")
               object_info += "\n" + " "*spaces + "Range" + class_or_axiom(axiom.component.ce, 1, 2)
           case "InverseObjectProperties":
               if str(axiom.component.first) == clss:
                   object_info += "\n" + " "*spaces + "Inverse Of" + class_or_axiom(axiom.component.second, 1, 2)
               elif str(axiom.component.second) == clss:
                   object_info += "\n" + " "*spaces + "Inverse Of" + class_or_axiom(axiom.component.first, 1, 2)
                   
           case "ObjectPropertyDomain":
               object_info += "\n" + " "*spaces + "Domain" + class_or_axiom(axiom.component.ce, 1, 2)
           case "FunctionalObjectProperty":
               object_info += "\n" + " "*spaces + "Is Functional"
           case "InverseFunctionalObjectProperty":
               object_info += "\n" + " "*spaces + "Is Inversely Functional"
           case "TransitiveObjectProperty":
               object_info += "\n" + " "*spaces + "Is Transitive"
           case "SymmetricObjectProperty":
               object_info += "\n" + " "*spaces + "Is Symmetric"
           case "ReflexiveObjectProperty":
               object_info += "\n" + " "*spaces + "Is Reflexive"
           case "IrreflexiveObjectProperty":
               object_info += "\n" + " "*spaces + "Is Irreflexive"
           case "AsymmetricObjectProperty":
               object_info += "\n" + " "*spaces + "Is Asymmetric"
       
   return object_info
           
           

def get_details_data(clss):
   entityaxioms = oe_onto.get_axioms_for_iri(clss)
   data_info = ""
   for axiom in entityaxioms:
       match type(axiom.component).__name__:
           case "DeclareDataProperty":
               pass
           case "EquivalentDataProperties":
               equivalence_content = get_equivalence_relation(clss,axiom)
               if not equivalence_content:
                   pass
               else:
                   data_info += equivalence_content
           case "SubDataPropertyOf":
               if str(axiom.component.sub) == clss:
                   data_info += "\n" + " "*spaces + "SubDataPropertyOf" + class_or_axiom(axiom.component.sup, 1, 2)
           case "DisjointDataProperties":
               data_info += "\n" + " "*spaces + "Is Disjoint With:"
               for expression in axiom.component.first:
                   if str(expression) == clss:
                       pass
                   else:
                       data_info += "\n" + " "*spaces*2 + class_or_axiom(expression, 0, 2)
           case "DataPropertyRange":
               data_info += "\n" + " "*spaces + "Range" + class_or_axiom(axiom.component.dr, 1, 2)
           case "DataPropertyDomain":
               data_info += "\n" + " "*spaces + "Domain" + class_or_axiom(axiom.component.ce, 1, 2)
           case "FunctionalDataProperty":
               data_info += "\n" + " "*spaces + "Is Functional"
       
   return data_info

def get_details_classes(clss):
   entityaxioms = oe_onto.get_axioms_for_iri(clss)
   class_info = ""
   for axiom in entityaxioms:
       if type(axiom.component).__name__ == "DeclareClass":
           pass
       elif type(axiom.component).__name__ == "EquivalentClasses":
           equivalence_content = get_equivalence_relation(clss,axiom)
           if not equivalence_content:
               pass
           else:
               class_info += equivalence_content
       elif type(axiom.component).__name__ == "SubClassOf":
           if str(axiom.component.sub) == clss:
               class_info += "\n" + " "*spaces + "SubClassOf" + class_or_axiom(axiom.component.sup, 1, 2)
       elif type(axiom.component).__name__ == "DisjointClasses":
           class_info += "\n" + " "*spaces + "Is Disjoint With:"
           for expression in axiom.component.first:
               if str(expression) == clss:
                   pass
               else:
                   class_info += "\n" + " "*spaces*2 + class_or_axiom(expression, 0, 2)
       elif type(axiom.component).__name__ == "DisjointUnion":
           if str(axiom.component.first) == clss:
               class_info += "\n" + " "*spaces + "DisjointUnionOf:" +  "\n" + " "*spaces*2
               for expression in axiom.component.second:
                   class_info += class_or_axiom(expression, 0, 2) + ","
               class_info = class_info[:-1]
       elif type(axiom.component).__name__ == "HasKey":
           class_info += "\n" + " "*spaces + "Is Target For Key:"
           for expression in axiom.component.vpe:
                class_info += "\n" + " "*spaces*2 + class_or_axiom(expression, 0, 2)
       
   return class_info


def get_label(clss):
   label = oe_onto.get_annotation(str(clss),"http://www.w3.org/2000/01/rdf-schema#label")
   if not label:
       label = str(clss)
       if "http://www.w3.org/2001/XMLSchema#" in label:
           return "xsd:" + label.split("#")[-1]
       if "http://www.w3.org/1999/02/22-rdf-syntax-ns#" in label:
           return "rdf:" + label.split("#")[-1]
       if "http://www.w3.org/2000/01/rdf-schema#" in label:
           return "rdfs:" + label.split("#")[-1]
       if "http://www.w3.org/2002/07/owl#" in label:
           return "owl:" + label.split("#")[-1]
       return str(clss)
   return label
   
   
   
   
def generate_basic_query(clssid):

   axioms_found = False
   nl_def_found = False
   semantic_def_found = False
   
   #Get axioms for class
   classaxioms = oe_onto.get_axioms_for_iri(clssid)
       
   if not classaxioms:
       return axioms_found, nl_def_found, semantic_def_found, ""
   axioms_found = True
   output_label = get_label(clssid)
   semantic_def = "Class: '" + str(output_label) + "'"
   
   nl_def = ""
   
   for axiom in classaxioms:
       ##If Axiom is annotation:
       if type(axiom.component).__name__ == "AnnotationAssertion":
           def_content = get_nl_def(axiom)
           ##If Annotation is not a definition
           if not def_content:
               pass
           else:
               nl_def += def_content
               nl_def_found = True
               entities = get_all_classes()
               for entity in entities:
                   if (' ' + get_label(entity) in nl_def) or (get_label(entity) + ' ' in nl_def):
                       entities_in_sem.append(str(entity))
                       #TODO
               
       ##If Axiom is EquivalentClass        
       elif type(axiom.component).__name__ == "EquivalentClasses":
           equivalence_content = get_equivalence_relation(clssid, axiom)
           if not equivalence_content:
               pass
           else:
               semantic_def += equivalence_content
               semantic_def_found = True
       
       ##Misc. Axioms
       else:
           pass
   query = ""
   query += "You are an ontology expert. Your task is to determine whether a natural-language definition and an OWL EquivalentTo axiom express the same semantic content. Your goal is to detect only real conceptual mismatches, not superficial differences. Compare only semantics, never wording. Treat logically equivalent structures as equivalent even when expressed differently (e.g., AND vs. intersection, OR vs. union, “some” restrictions, nested expressions, property–value forms, etc.). Do not interpret syntactic complexity (e.g., nested negations, unions written as sets) as semantic difference unless it changes the actual logical meaning. Focus on precision, and think step by step.\nAt the end of your answer, insert two line breaks followed either by 'Yes' if the contents of both match and 'No' if they do not.\nIf one contains more detailed information than the other, choose 'No'. For example, if you are provided with the following information:\n'The natural language definition is the following:\nA frog is an animal that quacks.\nThe equivalent-to axioms contains the following information:\nClass: 'frog'\n    EquivalentTo:\n        'animal'\n        and 'makesNoise' some ('quack')'\nThe last line of your reply should contain only the word 'Yes'.\nIf you are provided with the following information:\n'The natural language definition is the following:\nA cat is an animal that meows.\nThe equivalent-to axioms contains the following information:\nClass: 'cat'\n    EquivalentTo:\n        'pet'\n        and 'hunts' some ('mice')'\nThe last line of your reply should contain only the word 'No'.\nIf you are uncertain, choose 'No'. Do not add any further lines or symbols after this.\nYou may also be provided with some additional knowledge about other entities in the ontology appended to this prompt. If so, take this information into consideration as well.\nYou are analysing the class "
   query += output_label
   query += ". The natural language definition is the following:\n"
   query += nl_def
   query += "\nThe equivalent-to axioms contains the following information:\n"
   query += semantic_def
   
   return axioms_found, nl_def_found, semantic_def_found, query
   
def get_equivalence_relation(clssid, axiom):

   equivalence_relation = ""
   counter = 1
   
   if str(axiom.component.first[0]) == clssid:
       equivalence_relation += "\n" + " "*spaces + "EquivalentTo" + class_or_axiom(axiom.component.first[1], 1, 2)
   elif str(axiom.component.first[1]) == clssid:
       equivalence_relation += "\n" + " "*spaces + "EquivalentTo" + class_or_axiom(axiom.component.first[0], 1, 2)
   else:
       equivalence_relation = ""
   
   return equivalence_relation
       
       
       
       
def get_nl_def(axiom):
   definition_labels = "((h|H)as)*( )*(D|d)efinition" + "|" + "((I|i)s)*" + "(_)*( )*(d|D)efined( )*(_)*(a|A)s" 
   annotation_type = str(axiom.component.ann.ap.first)
   annotation_type_label = get_label(annotation_type)
   if re.search(definition_labels, annotation_type_label) or re.match(definition_labels, annotation_type):
       if hasattr(axiom.component.ann.av, 'literal'):
           annotation_content = axiom.component.ann.av.literal
           return annotation_content
   return ""
   
   
   
def class_or_axiom(superclass, indent, counter):
   ##print("__________________", superclass)
   
   ##If "indent>0": Add indents (for formatting)
   if(indent == 0):
       partial_def = ""
   else:
       partial_def = ":\n" + " "*(counter)*spaces
   
   ##If provided with a class (or IRI to a class) add the class label
   match type(superclass).__name__:
       case "Class" | "IRI" | "ObjectProperty" | "DataProperty":
           label = get_label(superclass)
           partial_def += "'" + label +"'"
           entities_in_sem.append(str(superclass))
       
   ##If provided with an Individual add the class label
       case "NamedIndividual" | "AnonymousIndividual":
           partial_def += "'" + get_label(superclass.first) + "'"
           entities_in_sem.append(str(superclass.first))
       
       case "ObjectComplementOf":
           partial_def += "not (" + class_or_axiom(superclass.first, 0, counter+1) + ")"
       
       case "ObjectOneOf":
           partial_def += object_of(superclass, indent, counter, ",")
       case "ObjectUnionOf":
           partial_def += object_of(superclass, indent, counter, "or")
       case "ObjectIntersectionOf":
           partial_def += object_of(superclass, indent, counter, "and")
       
       case "ObjectAllValuesFrom":
           partial_def += object_values(superclass, counter, "only")
       case "ObjectSomeValuesFrom":
           partial_def += object_values(superclass, counter, "some")
       case "ObjectExactCardinality":
           partial_def += object_values(superclass, counter, "exactly")
       case "ObjectMinCardinality":
           partial_def += object_values(superclass, counter, "min")
       case "ObjectMaxCardinality":
           partial_def += object_values(superclass, counter, "max")
       
       case "ObjectHasValue":
           relation = get_label(superclass.ope)
           relation_to = class_or_axiom(superclass.i, 0, counter)
           partial_def += "'" + relation + "' value " +  relation_to
           entities_in_sem.append(str(superclass.ope))
       
       
       case "DataHasValue":
           relation = get_label(superclass.dp)
           relation_to = str(superclass.l.literal)
           partial_def += "'" + relation + "' value " +  relation_to
           entities_in_sem.append(str(superclass.dp))
       
       case "DataMinCardinality":
           partial_def += data_axiom_to_string(superclass, "min")
       case "DataMaxCardinality":
           partial_def += data_axiom_to_string(superclass, "max")
       case "DataSomeValuesFrom":
           partial_def += data_axiom_to_string(superclass, "some")
       case "DataAllValuesFrom":
           partial_def += data_axiom_to_string(superclass, "only")
       case "DataExactCardinality":
           partial_def += data_axiom_to_string(superclass, "exactly")
       
       case "DataComplementOf":
           partial_def += "not " + datarange_to_string(superclass.first)
       case "Datatype":
           partial_def += datarange_to_string(superclass.first)
       
       case "DataOneOf":
           partial_def += literal_list(superclass.first, "")
       case "DataIntersectionOf":
           partial_def += "(" + literal_list(superclass.first, " and") + ")"
       case "DataUnionOf":
           partial_def += "(" + literal_list(superclass.first, " or") + ")"
   
   
   
       case _:
          print("__________________", type(superclass))
   
   return partial_def
   
def object_of(superclass, indent, counter, keyword):
   i = 0
   list_of_classes = superclass.first
   partial_def = ""
   if keyword == ",":
       partial_def += "{"
   else:
       keyword = "\n" + " "*(counter)*spaces + keyword + " "
   for clss in list_of_classes:
       if(i > 0):
           partial_def += keyword + class_or_axiom(clss,0,counter+1)
       else:
           if (keyword != ",") and (indent == 0):
               partial_def += "\n" + " "*(counter)*spaces
           partial_def += class_or_axiom(clss,0,counter+1)
           i += 1
   
   if keyword == ",":
       partial_def += "}"
       
   return partial_def
   
   
def object_values(superclass, counter, keyword):
   relation = get_label(superclass.ope)
   relation_to = class_or_axiom(superclass.bce, 0, counter)
   
   if hasattr(superclass, 'n'):
       keyword +=  " " + str(superclass.n)
       
   partial_def = "'" + relation + "' " + keyword + " (" +  relation_to + ")"
   entities_in_sem.append(str(superclass.ope))
   return partial_def
    
    
def data_axiom_to_string(superclass, keyword):
   if keyword:
       keyword += " "
   if hasattr(superclass, 'n'):
       keyword += str(superclass.n) + " "
       
   relation = get_label(superclass.dp)
   relation_to = datarange_to_string(superclass.dr)
   
   this_axiom = "'" + relation + "' "+ keyword + "(" +  relation_to + ")"
   entities_in_sem.append(str(superclass.dp))
   return this_axiom
   
   
def datarange_to_string(dr):
   
   relation_to_str = dr
   if(type(dr).__name__ == "list"):
       relation_to_str = literal_list(dr, "")
   elif(type(dr).__name__ == "DataOneOf"):
       relation_to_str = literal_list(dr.first, "")
   else:
       relation_to_str = class_or_axiom(dr, 0, 0)
   return relation_to_str

   
def literal_list(total_list, seperator):
   list_string = "{"
   if not seperator:
       seperator = ","
   for item in total_list:
       #print("_____________________", item)
       if hasattr(item, 'literal'):
           list_string += '"' + item.literal + '"' + seperator + " " 
       else:
           list_string += class_or_axiom(item, 0, 0) + seperator + " " 
   
   remove = 1 + len(seperator)    
   remove = remove*(-1)
   list_string = list_string[:remove]
   list_string += "}"
   return list_string
