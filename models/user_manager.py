import json
import typing as t

from .user import User


class UserManager:
    def __init__(self):
        # TODO: Read from database.
        with open('data/users.json', 'r') as file:
            data = json.load(file)
        self.users = {}

        for k, v in data.items():
            self.users[v["id"]] = User(
                name=v["name"],
                password=v["password"],
                tu_truyen=v["favorites"],
                last_read=v['last_read']
            )
            self.users[v["id"]].id = v["id"]

    def check(self, name: str, password: str):
        for user in self.users.values():
            if user.name.lower() == name.lower() and user.password == password:
                return user
        return None

    def register(self, name: str, password: str):
        user = User(name, password)
        self.users[str(user.id)] = user
        # Add to database.
        self.update_database()
        return user

    def check_exist(self, name):
        for user_id, user in self.users.items():
            if user.name.lower() == name.lower():
                return True
        return False

    def update_database(self):
        with open('data/users.json', 'w+') as file:
            json.dump({str(u.id): u.to_dict() for u in self.users.values()}, file, indent=2)
