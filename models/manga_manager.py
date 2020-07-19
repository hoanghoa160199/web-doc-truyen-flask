import os
from .manga import Manga
import typing as t


class MangaManager:
    def thêm(self): ...
    def sửa(self): ...
    def xóa(self): ...

    def __init__(self):
        self.danh_sách_truyện: t.Dict[str, Manga] = {}
        self.update()

    def tìm_truyện(self, tên):
        kết_quả = []
        for tên_folder, truyện in self.danh_sách_truyện.items():
            if tên.casefold() in truyện.tên.casefold():
                kết_quả.append(truyện)
        return kết_quả

    def tìm_thể_loại(self, thể_loại):
        return [
            truyện
            for name, truyện in self.danh_sách_truyện.items()
            if thể_loại.casefold() in truyện.thể_loại
        ]

    def tìm_tác_giả(self, thể_loại):
        return [
            truyện
            for the_loai, truyện in self.danh_sách_truyện.items()
            if thể_loại.casefold() in truyện.tác_giả.casefold()
        ]

    def tìm_năm(self, năm):
        return [
            truyện
            for nam, truyện in self.danh_sách_truyện.items()
            if int(năm) == truyện.năm
        ]

    def update(self):
        folders = os.listdir('truyện')
        for tên_folder in folders:
            manga = Manga(tên_folder)
            self.danh_sách_truyện[manga.tên_folder] = manga
