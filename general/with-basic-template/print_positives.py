##Imports

import os
import json

import re

def process_llm_reply(reply):
   lastline = reply.splitlines()[-1]
   pos = 0
   neg = 0
   lastline = re.sub(r"now", "", lastline)
   lastline = re.sub(r"not", "", lastline)
   
   if "yes" in lastline or "Yes" in lastline:
       neg = 1
   if "no" in lastline or "No" in lastline:
       pos = 1
   if (pos+neg) == 1:
       if pos:
           return 1
       if neg:
           return 0
       else:
           return -1
   return -1
 
def read_basic(file_name):
   
   errors_found = []
   if not os.path.exists(file_name):
       print("No results to evaluate!")
    
   with open(file_name, "r") as outfile:
       #load json content and add new data
       existing_content = json.load(outfile)
       entries = existing_content["extractionInfo"]
       for entry in entries:
           if not "iri" in entry:
               continue
           if entry["nl_definition_found"] and entry["semantic_definition_found"]:
               classification = process_llm_reply(entry["reply_basic_query"])
               if classification == 1:
                   errors_found.append(entry["iri"])
               #Treat unsure/formatting mistakes as positives ("there is a discrepency")
               elif classification == -1:
                   errors_found.append(entry["iri"])
   
   return errors_found
