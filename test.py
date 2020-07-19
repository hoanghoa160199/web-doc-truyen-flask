import json
from models import User
with open('data/users.json', 'r') as file:
    data = json.load(file)
users = {}
for k, v in data.items():
    users[v["id"]] = User(name=v["name"], password=v["password"])
    users[v["id"]].id = v["id"]
print(users)
