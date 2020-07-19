import json
import os

PATH = "truyện"
MISSING_INFO = 'Chưa cập nhật'


class Manga:
    def __init__(self, tên_folder: str):
        self.tên_folder = tên_folder
        try:
            with open(f"{PATH}/{tên_folder}/info.json", 'r', encoding='utf-8') as file:
                info = json.load(file)
        except FileNotFoundError:
            info = {}
        self.tác_giả = info.get('tác_giả', MISSING_INFO)
        self.thể_loại = info.get('thể_loại', [MISSING_INFO])
        self.năm = info.get('năm', MISSING_INFO)
        self.rank = info.get('điểm', MISSING_INFO)
        self.tên = info.get('tên', tên_folder)
        self.điểm = info.get('điểm', 0)
        chương = [f for f in os.scandir(f"{PATH}/{tên_folder}") if os.path.isdir(f)]
        chương = {folder.name.replace('chapter-', ''): folder for folder in chương}
        self.chương = dict(sorted(chương.items(), key=lambda p: int(p[0])))

    def tìm_trang(self, số_chương):
        return sorted(os.listdir(self.chương[str(số_chương)]), key=lambda c: int(c.replace('.jpg', '')))

    def __repr__(self):
        return f"Manga({self.tên!r} - {len(self.chương)} chuong)"
