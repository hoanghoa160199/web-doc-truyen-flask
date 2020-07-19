import random


class Base:
    def __eq__(self, value):
        return isinstance(self, type(value))


class Rock(Base):
    def __lt__(self, value):
        return isinstance(value, Paper)


class Paper(Base):
    def __lt__(self, value):
        return isinstance(value, Scissors)


class Scissors(Base):
    def __lt__(self, value):
        return isinstance(value, Rock)


while (user := input('Chon R P S:')) != '':
    if user.lower() not in 'rps':
        print('Khong hop le')
        continue

    user = [Rock(), Paper(), Scissors()]['RPS'.index(user.upper())]

    computer = random.choice([Rock(), Paper(), Scissors()])

    if user == computer:
        print('Hoa')
    elif user < computer:
        print('Thua')
    else:
        print('Thang')
