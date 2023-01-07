import requests

# kserve endpoint
endpoint = "http://localhost:5000/predict"

data = {"input": [r"\d+", "He is 777& years old"]}

headers = {"Content-Type": "application/json"}

response = requests.post(endpoint, json=data, headers = headers)

print(response.json())