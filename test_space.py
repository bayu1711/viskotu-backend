import requests
import json
res = requests.get('http://localhost:8000/api/v1/spaces/ee0b3fe1-0345-42f9-8a04-6f8ac0ec512d/')
print(json.dumps(res.json(), indent=2))
