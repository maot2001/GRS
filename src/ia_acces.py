import requests
import json

with open('llama_key.txt','r') as file:
    LLAMA_API_KEY = file.read()

def llama_acces(message, code=False):
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
        "model": "accounts/fireworks/models/llama-v3p1-405b-instruct",
        "max_tokens": 4096,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
                {"role": "user", "content": message}
            ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": LLAMA_API_KEY
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        
        response = json.loads(response.text)
        response = f"{response['choices'][0]['message']['content']}"
        try:
            init = response.index('{')
            end = response.index('}')
                
            if code:
                init_code = response.index('```')
                end_code = response[init_code+3:].index('```')
                codex = response[init_code + 3 : init_code + 3 + end_code]
                codex = codex.replace('python', '')
                
            response = json.loads(response[init:end+1])

            if code: return response, codex
            return response
        except Exception as e:
            print(e)

            if code: return None, None
            return None