import requests
import json

def call_LLM(query):

   url = "http://localhost:8000/api/generate"

   headers = {
       "Content-Type": "appliction/json"
   }

   actual_response = ""
   
   data = {
       "model": "llama4:scout",
       "prompt": query,
       "stream": False,
   }
   
       #"model": "llama4:scout",
       #"model": "magistral",
   
   response = requests.post(url, headers=headers, data=json.dumps(data))
   
   if response.status_code == 200:
       response_text = response.text
       data = json.loads(response_text)
       actual_response = data["response"]
       #print(actual_response)
   else:
        print(response.status_code)
   return actual_response     
