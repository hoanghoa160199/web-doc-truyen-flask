from uuid import uuid4


class User:
    def __init__(self, ten: str, tuoi: int, tu_truyen: list):
        self.ten = ten
        self.id = uuid4()
        self.tuoi = tuoi
        self.tu_truyen = tu_truyen

    def __str__(self):
        return f"User(id={self.id!r}, ten={self.ten!r}, tuoi={self.tuoi!r}, tu_truyen={self.tu_truyen!r})"


data = {
    'a': {
        'id': 'a',
        'ten': 'Hoa',
        'tuoi': 200,
        "tu_truyen": []
    },
    'b': {
        'id': 'b',
        'ten': 'Phuoc',
        'tuoi': 15,
        "tu_truyen": []
    },
    'c': {
        'id': 'c',
        'ten': 'Trang',
        'tuoi': 14,
        "tu_truyen": []
    },
    'd': {
        'id': 'd',
        'ten': 'Tai',
        'tuoi': 30,
        "tu_truyen": []
    },
}

user = User("Gin", 1, ["áddas"])
print(user)

for x, y in data.items():
    user = User(y["ten"], y["tuoi"], y["tu_truyen"])
    user.id = y["id"]
    print(x)
