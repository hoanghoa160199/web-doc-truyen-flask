from datetime import datetime


class Comment:
    def __init__(self, user_id, manga_id, content):
        self.user_id = user_id
        self.manga_id = manga_id
        self.content = content
        self.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'manga_id': self.manga_id,
            'content': self.content,
            'time': self.time,
        }
