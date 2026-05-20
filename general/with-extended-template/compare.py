import ollama_api
import ontology_extraction
import os
import json
import datetime

def check_entity(clssid):

   basic_reply = "N/A"
   extended_reply = "N/A"
   reply_time = ""

##Generate Query
   exists, nl, equivalence, extended_query = ontology_extraction.generate_queries(clssid)
   if not exists:
      print("This class does not exist.")
   elif nl and equivalence:
      #print("******************************************")
      #print(extended_query)
      #print("******************************************")
      #print(basic_query)
      reply_time = f'{datetime.datetime.now():%Y-%m-%d %H:%M:%S%z}'
      extended_reply = ollama_api.call_LLM(extended_query)
   else:
      extended_query = "N/A"
       

   newData = {
      "iri": clssid,
      "datetime": reply_time,
      "nl_definition_found": bool(nl),
      "semantic_definition_found": bool(equivalence),
      "extended_query": extended_query,
      "reply_extended_query": extended_reply
   }


   #TODO different out-files 
   filename = "results.json"
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
      
def check_all():
   entities = ontology_extraction.get_all_classes()
   for entity in entities:
       check_entity(entity)
