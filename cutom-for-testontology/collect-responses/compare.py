import ollama_api
import ontology_extraction
import os
import json
import datetime

def check_entity(clssid, nmbr, letter):

   basic_reply = "N/A"
   extended_reply = "N/A"
   reply_time = ""

##Generate Query
   exists, nl, equivalence, basic_query, extended_query = ontology_extraction.generate_queries(clssid, nmbr)
   if not exists:
      print("This class does not exist.")
   elif nl and equivalence:
      #print("******************************************")
      #print(extended_query)
      #print("******************************************")
      #print(basic_query)
      reply_time = f'{datetime.datetime.now():%Y-%m-%d %H:%M:%S%z}'
      basic_reply = ollama_api.call_LLM(basic_query)
      extended_reply = ollama_api.call_LLM(extended_query)
   else:
      print("Definition not found: ")
      if not nl:
          print("  - natural language definition")
          #print(extended_query)
      if not equivalence:
          print("  - Equivalence Relation")
          #print(basic_query)
       

   newData = {
      "iri": clssid,
      "datetime": reply_time,
      "nl_definition_found": bool(nl),
      "semantic_definition_found": bool(equivalence),
      "basic_query": basic_query,
      "reply_basic_query": basic_reply,
      "extended_query": extended_query,
      "reply_extended_query": extended_reply
   }


   #TODO different out-files 
   filename = "results-"
   if nmbr < 10:
       filename += "0"
   filename += str(nmbr) + letter + ".json"
   if not os.path.exists(filename):
       with open(filename, "w") as outfile:
           outfile.write('{"extractionInfo": [{}]}')
   #TODO different out-files 
   with open(filename, "r+") as outfile:
      #load json content and add new data
      existing_content = json.load(outfile)
      existing_content["extractionInfo"].append(newData)
      #write to json file
      outfile.seek(0)
      json.dump(existing_content, outfile, indent=4)
      
def check_all(nmbr, letter):
   entities = ontology_extraction.get_all_classes()
   for entity in entities:
       check_entity(entity, nmbr, letter)
