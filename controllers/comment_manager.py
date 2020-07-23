import json

from models import Comment


class CommentManager:
    def __init__(self):
        self.danh_sách_bình_luận = []
        self.đọc_từ_database()

    def đọc_từ_database(self):
        with open('data/comments.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for value in data:
            bình_luận = Comment(value['user_id'], value['manga_id'], value['content'])
            bình_luận.time = value['time']
            self.danh_sách_bình_luận.append(bình_luận)

    def ghi_vào_database(self):
        with open('data/comments.json', 'w+', encoding='utf-8') as file:
            json.dump([bl.to_dict() for bl in self.danh_sách_bình_luận], file, indent=2)

    def thêm_bình_luận(self, user_id, manga_id, content):
        comment = Comment(user_id, manga_id, content)
        self.danh_sách_bình_luận.append(comment)
        self.ghi_vào_database()

    def tìm_bình_luận_theo_truyện(self, manga_id):
        return [
            bình_luận
            for bình_luận in self.danh_sách_bình_luận
            if bình_luận.manga_id == manga_id
        ]

    def tìm_bình_luận_theo_user(self, user_id):
        return [
            bình_luận
            for bình_luận in self.danh_sách_bình_luận
            if bình_luận.user_id == user_id
        ]
