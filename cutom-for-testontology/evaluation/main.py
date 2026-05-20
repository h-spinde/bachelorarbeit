##Imports

import pyhornedowl

import os
import json

import csv

import re

no_def = ["#movie", "#breezeberry"]
no_nl = ["#paraberry"]
no_axiom = ["#lime"]
more_in_axiom = ["#firelemon", "#grape", "#snowlemon", "#starfruit", "#tree"]
more_in_nl = ["#banana", "#potato", "#salad", "#sweetcherry", "#tophberry", "#napple"]
no_contradictions = ["#edible", "#fruit_salad", "#kiwi", "#orange", "#wine", "#onion", "#hazlenut", "#dragon"]
contradictions = ["#vegetable"]

axiom_explicit = ["#berry", "#book", "#dragonfruit", "#durian", "#mango", "#pear", "#strawberry", "#lemon", "#juice"]
nl_explicit = ["#cherry", "#parasite", "#plumb", "#tomato"]
perfect = ["#fruit", "#tangerine", "#apple", "#medium", "#obscurry", "#favourite_food", "#blueberry", "#pepper"]


fields_prompt_eval = ['FileName/RunID', 'True Positives', 'True Negatives', 'False Positives', 'False Negatives', ' ', 'FP: Explicit in Axiom', 'FP: Explicit in NL', 'FP: Perfect Match', ' ', 'FN: More Info in Axiom', 'FN:More Info in NL', 'FN:No Contradictions', 'FN:Contradictions', ' ', 'Precision', 'Recall', 'F1-Score', ' ', '% of Explicit in Axiom Wrong', '% of Explicit in NL Wrong', '% Of Perfect Match Wrong', ' ', '% of More in Axiom Wrong', '% of More in NL Wrong', '% of No Contradictions Wrong', '% of Contradictions Wrong', ' ', '% of Errors Ex in Ax', '% of Errors Ex in NL', '% of Errors Perfect', '% of Errors More in Axiom', '% of Errors More in NL', '% of Errors No Contradictions', '% of Errors Contradictions']

def init(ontology_name):
    global oe_onto
    oe_onto = pyhornedowl.open_ontology(ontology_name)
    
def process_llm_reply(reply, filename):
   lastline = reply.splitlines()[-1]
   pos = 0
   neg = 0
   neutral = 0
   
   if "yes" in lastline or "Yes" in lastline:
       if (re.search(r'jsons/results-0([1-7])', filename) is not None) or filename.startswith("jsons/results-14"): #filename.startswith("results-0"):
           pos = 1
       else:
           neg = 1
   if "no" in lastline or "No" in lastline:
       if (re.search(r'jsons/results-0([1-7])', filename) is not None) or filename.startswith("jsons/results-14"): #filename.startswith("results-0"):
           neg = 1
       else:
           pos = 1
   if "unsure" in lastline or "Unsure" in lastline:
       neutral = 1
   if (pos+neg+neutral) == 1:
       if pos:
           return 1
       if neg:
           return 0
       else:
           return -1
   #else:
   #    print("\n\n" + reply)
   #    user_translation: int = input("Enter '1' if descrepencies, '0' if none, '-1' if unclear: ")
   #    return user_translation
   return -1
       

def get_discrapency(clss):
   entityaxioms = oe_onto.get_axioms_for_iri(clss)
   for axiom in entityaxioms:
       if type(axiom.component).__name__ == "AnnotationAssertion":
           annotation_type = str(axiom.component.ann.ap.first)
           if annotation_type == "http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#hasDiscrepancy":
               if hasattr(axiom.component.ann.av, 'literal'):
                   annotation_content = axiom.component.ann.av.literal
                   if annotation_content == "true":
                       return 1
                   if annotation_content == "false":
                       return 0
   
   return -1

def read_json(clss, file_name):

   #if not os.path.exists("results-" + file_id + ".json"):
   if not os.path.exists(file_name):
       print("No results to evaluate!")
    
   #with open("results-" + file_id + ".json", "r") as outfile:
   with open(file_name, "r") as outfile:
      #load json content and add new data
      existing_content = json.load(outfile)
      entries = existing_content["extractionInfo"]
      for entry in entries:
          if not "iri" in entry:
              continue
          if entry["iri"] == clss:
              if extended:
                  return process_llm_reply(entry["reply_extended_query"], file_name)
              else:
                  return process_llm_reply(entry["reply_basic_query"], file_name)
   return -1

def find_prompt_runs(prompt_nmbr):
   rows = []
   i = 0

   all_files = os.listdir("jsons/")
   for result_file in all_files:
        if result_file.startswith("results-"+prompt_nmbr):
            rows.append([])
            run_results = evaluate_run(result_file)
            rows[i].append(result_file)
            rows[i].append(run_results["true positives"])
            rows[i].append(run_results["true negatives"])
            #rows[i].append("=SUM(G"+str(i+2)+":I"+str(i+2)+")")
            rows[i].append(sum(run_results["false positives"].values()))
            #rows[i].append("=SUM(K"+str(i+2)+":N"+str(i+2)+")")
            rows[i].append(sum(run_results["false negatives"].values()))
            rows[i].append(" ")
            rows[i].append(run_results["false positives"]["explicit in axiom"])
            rows[i].append(run_results["false positives"]["explicit in nl"])
            rows[i].append(run_results["false positives"]["perfect match"])
            rows[i].append(" ")
            rows[i].append(run_results["false negatives"]["more info in axiom"])
            rows[i].append(run_results["false negatives"]["more info in nl"])
            rows[i].append(run_results["false negatives"]["no contradictions"])
            rows[i].append(run_results["false negatives"]["contradictions"])
            rows[i].append(" ")
            #rows[i].append("=B"+str(i+2)+"/(B"+str(i+2)+"+D"+str(i+2)+")")
            try:
                precision = run_results["true positives"]/(run_results["true positives"]+sum(run_results["false positives"].values()))
            except ZeroDivisionError:
                precision = 0
            rows[i].append(precision)
            #rows[i].append("=B"+str(i+2)+"/(B"+str(i+2)+"+E"+str(i+2)+")")
            try:
                recall = run_results["true positives"]/(run_results["true positives"]+sum(run_results["false negatives"].values()))
            except ZeroDivisionError:
                recall = 0
            rows[i].append(recall)
            #rows[i].append("=(2*P"+str(i+2)+"*Q"+str(i+2)+")/(P"+str(i+2)+"+Q"+str(i+2)+")")
            try:
                rows[i].append(2*precision*recall/(precision+recall))
            except ZeroDivisionError:
                rows[i].append(0)
            rows[i].append(" ")
            rows[i].append(100*run_results["false positives"]["explicit in axiom"]/9)
            rows[i].append(100*run_results["false positives"]["explicit in nl"]/4)
            rows[i].append(100*run_results["false positives"]["perfect match"]/8)
            rows[i].append(" ")
            rows[i].append(100*run_results["false negatives"]["more info in axiom"]/5)
            rows[i].append(100*run_results["false negatives"]["more info in nl"]/6)
            rows[i].append(100*run_results["false negatives"]["no contradictions"]/8)
            rows[i].append(100*run_results["false negatives"]["contradictions"])
            rows[i].append(" ")
            total_errors = sum(run_results["false positives"].values()) + sum(run_results["false negatives"].values())
            try:
                rows[i].append(100*run_results["false positives"]["explicit in axiom"]/total_errors)
                rows[i].append(100*run_results["false positives"]["explicit in nl"]/total_errors)
                rows[i].append(100*run_results["false positives"]["perfect match"]/total_errors)
                rows[i].append(100*run_results["false negatives"]["more info in axiom"]/total_errors)
                rows[i].append(100*run_results["false negatives"]["more info in nl"]/total_errors)
                rows[i].append(100*run_results["false negatives"]["no contradictions"]/total_errors)
                rows[i].append(100*run_results["false negatives"]["contradictions"]/total_errors)
            except ZeroDivisionError:
                for z in range(0,7):
                    rows[i].append("N.A.")
            i += 1
            
   rows.append([])
   rows[i].append("Average")
   '''rows[i].append("=SUM(B2:B"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(C2:C"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(D2:D"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(E2:E"+str(i+1)+")/"+str(i))
   rows[i].append(" ")
   rows[i].append("=SUM(G2:G"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(H2:H"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(I2:I"+str(i+1)+")/"+str(i))
   rows[i].append(" ")
   rows[i].append("=SUM(K2:K"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(L2:L"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(M2:M"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(N2:N"+str(i+1)+")/"+str(i))
   rows[i].append(" ")
   rows[i].append("=SUM(P2:P"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(Q2:Q"+str(i+1)+")/"+str(i))
   rows[i].append("=SUM(R2:R"+str(i+1)+")/"+str(i))'''
   # Caluclate averages and add in extra line
   for j in range(1,35):
       if j in[5, 9, 14, 18, 22, 27]:
       #if j == 5 or j == 9 or j == 14 or j == 18 or j == 22:
           rows[i].append(" ")
           continue
       average = 0
       for k in range(0,i):
           #print(str(k) + ", " + str(j) + ": " + str(rows[k][j]))
           if rows[k][j] == "N.A.":
               continue
           average+= rows[k][j]
       rows[i].append(average/i)
            
   filename = "data/prompt-"+prompt_nmbr+"/eval-prompt-"+prompt_nmbr
   if extended:
       filename += "_extended"
   else:
       filename += "_basic"
   filename += ".csv"
            
   with open(filename, 'w') as csvfile:
       csvwriter = csv.writer(csvfile)        # Create writer object
       csvwriter.writerow(fields_prompt_eval)             # Write header
       csvwriter.writerows(rows)
            
   #print(os.listdir("data/prompt-"+nmbr+"/prompt-"+nmbr+"-runs"))
   
def evaluate_run(file_name):
   #print(file_name)
   run_id = file_name.replace("results-","")
   run_id = run_id.replace(".json","")
   nmbr = run_id[:2]
    
   #tp = 0
   #tn = 0
   #fp = 0
   #fn = 0
   
   result_classification = { "true positives":0,
                             "true negatives":0,
                             "false negatives": { "more info in axiom":0,
                                                  "more info in nl":0,
                                                  "no contradictions":0,
                                                  "contradictions":0 },
                             "false positives": { "explicit in axiom":0,
                                                  "explicit in nl":0,
                                                  "perfect match":0 }}
    
   more_in_axiom_wrong = 0
   more_in_nl_wrong = 0
   no_contradictions_wrong = 0
   contradictions_wrong = 0
    
   #axiom_explicit_wrong = 0
   #nl_explicit_wrong = 0
   #perfect_wrong = 0
    
   fields_run = ['IRI', 'LLM', 'Expected', 'Match']
   rows_run = []
   i = 0
    
   precision = 0
   recall = 0
   f1 = 0
    
   entities = oe_onto.get_classes()
   ignore = ['http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#movie', 'http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#breezeberry', 'http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#paraberry', 'http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#lime']
    
   for entity in entities:
       if entity in ignore:
           continue
       rows_run.append([])
       rows_run[i].append(entity)
       expected_answer = get_discrapency(entity)
       
       llm_answer = read_json(entity, "jsons/" + file_name)
       rows_run[i].append(llm_answer)
       rows_run[i].append(expected_answer)
       if (expected_answer == 0):
           if (llm_answer == 0):
               rows_run[i].append(1)
               result_classification["true negatives"] += 1
           else:
               rows_run[i].append(0)
               #print(entity)
               if entity.endswith(tuple(axiom_explicit)):
                   result_classification["false positives"]["explicit in axiom"] += 1
               elif entity.endswith(tuple(nl_explicit)):
                   result_classification["false positives"]["explicit in nl"] += 1
               elif entity.endswith(tuple(perfect)):
                   result_classification["false positives"]["perfect match"] += 1
       else:
           if (llm_answer == 0):
               rows_run[i].append(0)
               if entity.endswith(tuple(more_in_axiom)):
                   result_classification["false negatives"]["more info in axiom"] += 1
               elif entity.endswith(tuple(more_in_nl)):
                   result_classification["false negatives"]["more info in nl"] += 1
               elif entity.endswith(tuple(no_contradictions)):
                   result_classification["false negatives"]["no contradictions"] += 1
               elif entity.endswith(tuple(contradictions)):
                   result_classification["false negatives"]["contradictions"] += 1
           else:
               rows_run[i].append(1)
               result_classification["true positives"] += 1
               
       i += 1
   
   #filename = "data/prompt-"+nmbr+"/eval-prompt-"+nmbr+".csv"
   filename = "data/prompt-"+nmbr+"/prompt-"+nmbr+"-runs_"
   if extended:
        filename += "extended"
   else:
        filename += "basic"
   filename += "/" + "eval-prompt-"+run_id
   if extended:
       filename += "_extended"
   else:
       filename += "_basic"
   filename += ".csv"
   #filename = "eval.csv"
   with open(filename, 'w') as csvfile:
       csvwriter = csv.writer(csvfile)        # Create writer object
       csvwriter.writerow(fields_run)             # Write header
       csvwriter.writerows(rows_run)
       
   if result_classification["true positives"]+sum(result_classification["false positives"].values()) > 0:
       precision = result_classification["true positives"]/(result_classification["true positives"]+sum(result_classification["false positives"].values()))
   if result_classification["true positives"]+sum(result_classification["false negatives"].values()) > 0:
       recall = result_classification["true positives"]/(result_classification["true positives"]+sum(result_classification["false negatives"].values()))
   if (precision+recall)>0:
       f1 = 2*precision*recall/(precision+recall)
       
   #print("F1 Score: " + str(f1))
   #print("False Negatives: " + str(sum(result_classification["false negatives"].values())))
   return result_classification

def evaluate_prompt(prompt_nmbr):

    parent_folder = "data/prompt-"+prompt_nmbr
    sub_folder = parent_folder+"/prompt-"+prompt_nmbr+"-runs"
    if extended:
        sub_folder += "_extended"
    else:
        sub_folder += "_basic"
    
    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)
        
    find_prompt_runs(prompt_nmbr)
    
def start_interaction():

    x= "sfo"
    ontology_name = "../../../ontologies/" + x + "/" + x + ".owx"
    init(ontology_name)

    if not os.path.exists("data"):
        os.makedirs("data")

    for i in range(2,10):
       evaluate_prompt("0" + str(i))
    for i in range(10,21):
       evaluate_prompt(str(i))

def compare_prompts():
    rows = []
    for x in range(2,10):
        rows.append(retrieve_line("0" + str(x), "_basic"))
        rows.append(retrieve_line("0" + str(x), "_extended"))
    for x in range(10,21):
        rows.append(retrieve_line(str(x), "_basic"))
        rows.append(retrieve_line(str(x), "_extended"))
    return rows

def retrieve_line(file_id, version):
   filename = "data/prompt-"+file_id+"/eval-prompt-"+ file_id + version + ".csv"
   with open(filename, 'r') as csvfile:
       final_line = csvfile.readlines()[-1]
   final_line = final_line.replace("Average",version.replace("_","")+": "+file_id)
   return final_line

def class_error_rates():
   rows = []
   nmbr = ""
   mode = "extended"
   letter = ""
   iri_gen = "http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#"
   classes = { "firelemon":1, "grape":2, "snowlemon":3, "starfruit":4, "tree":5, "banana":6, "potato":7, "salad":8, "sweetcherry":9, "tophberry":10, "napple":11, "edible":12, "fruit_salad":13, "kiwi":14, "orange":15, "wine":16, "onion":17, "hazlenut":18, "dragon":19, "vegetable":20, "berry":21, "book":22, "dragonfruit":23, "durian":24, "mango":25, "pear":26, "strawberry":27, "lemon":28, "juice":29, "cherry":30, "parasite":31, "plumb":32, "tomato":33, "fruit":34, "tangerine":35, "apple":36, "medium":37, "obscurry":38, "favourite_food":39, "blueberry":40, "pepper":41 }
   rows.append(["", *classes])
   for x in range(2,21):
       if x == 1:
           rows.append([])
           rows[1].append("Expected")
           for y in range (2,44):
               rows[1].append("")
           with open("data/prompt-01/prompt-01-runs_basic/eval-prompt-01a_basic.csv", 'r') as csvfile:
               lines = csvfile.readlines()
               for line in lines:
                   if line.startswith("IRI"):
                       continue
                   cells = line.split(",")
                   entity_name = cells[0].replace(iri_gen, "")
                   rows[1][classes[entity_name]] = cells[2]
       #rows.append([])
       #for y in range (1,48):
       #    rows[x+1].append("")
       if x<10:
           nmbr = "0" + str(x)
       else:
           nmbr = str(x)
       all_files = os.listdir("jsons/")
       for result_file in all_files:
           if result_file.startswith("results-"+nmbr):
               letter = result_file.replace("results-","")
               letter = letter.replace(".json","")
               letter = letter.replace(nmbr,"")
               rows.append(read_run_files(nmbr, letter, "extended"))
               rows.append(read_run_files(nmbr, letter, "basic"))
       '''filename = "data/prompt-"+nmbr+"/prompt-"+nmbr+"-runs_" + mode + "/eval-prompt-"+nmbr+letter+"_" + mode + ".csv"
       rows[x+1][0] = nmbr+letter + " "
       rows[x+1][0] += mode'''
       with open(filename, 'r') as csvfile:
           lines = csvfile.readlines()
       for line in lines:
           if line.startswith("IRI"):
               continue
           cells = line.split(",")
           #classes[cells[0].replace(iri_gen, "")]
           entity_name = cells[0].replace(iri_gen, "")
           '''if x==1:
               rows[1][classes[entity_name]] = cells[2]
           rows[x+1][classes[entity_name]] = cells[1]'''
   print(rows)
   #rows.append(read_run_files())
   target_file = "class_analysis.csv"
   with open(target_file, 'w') as csvfile:
       csvwriter = csv.writer(csvfile)        # Create writer object
       csvwriter.writerows(rows)
   
   #TODO add "basic" support, add "letter" support
   
  
def read_run_files(nmbr, letter, mode):
   iri_gen = "http://www.semanticweb.org/spinde/ontologies/2025/5/strange-fruits-ontology#"
   classes = { "firelemon":1, "grape":2, "snowlemon":3, "starfruit":4, "tree":5, "banana":6, "potato":7, "salad":8, "sweetcherry":9, "tophberry":10, "napple":11, "edible":12, "fruit_salad":13, "kiwi":14, "orange":15, "wine":16, "onion":17, "hazlenut":18, "dragon":19, "vegetable":20, "berry":21, "book":22, "dragonfruit":23, "durian":24, "mango":25, "pear":26, "strawberry":27, "lemon":28, "juice":29, "cherry":30, "parasite":31, "plumb":32, "tomato":33, "fruit":34, "tangerine":35, "apple":36, "medium":37, "obscurry":38, "favourite_food":39, "blueberry":40, "pepper":41 }
   run_row = []
   run_row.append(nmbr+letter + " " + mode)
   for y in range (1,42):
       run_row.append("")
   filename = "data/prompt-"+nmbr+"/prompt-"+nmbr+"-runs_" + mode + "/eval-prompt-"+nmbr+letter+"_" + mode + ".csv"
   with open(filename, 'r') as csvfile:
           lines = csvfile.readlines()
   for line in lines:
       if line.startswith("IRI"):
               continue
       cells = line.split(",")
       #classes[cells[0].replace(iri_gen, "")]
       entity_name = cells[0].replace(iri_gen, "")
       run_row[classes[entity_name]] = cells[1]
   return run_row

extended = bool(False)
start_interaction()
extended = bool(True)
start_interaction()

filename = "data/compare.csv"
compare_rows = compare_prompts()
with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields_prompt_eval)
    for line in compare_rows:
        csvfile.write(line)

class_error_rates()
