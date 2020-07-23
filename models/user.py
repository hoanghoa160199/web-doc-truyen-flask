from __future__ import annotations

import os
import random
from uuid import uuid4

from flask_login import UserMixin

AVATARS = [f.name for f in os.scandir('images/avatars')]


class User(UserMixin):
    def __init__(
            self, name: str, password: str,
            tu_truyen: list = None, last_read: dict = None
    ):
        self.id = uuid4()
        self.name = name
        self.password = password
        self.tu_truyen = tu_truyen or []
        self.last_read = last_read or {}
        self.avatar = random.choice(AVATARS)

    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'name': self.name,
            'password': self.password,
            'favorites': self.tu_truyen,
            'last_read': self.last_read,
            'avatar': self.avatar,
        }

    def __repr__(self):
        return f"Tên:{self.name} ID:{self.id}"
