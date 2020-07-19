import os
from .manga import Manga, MISSING_INFO
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

    def gợi_ý_theo_tác_giả(self, truyện_hiện_tại: Manga):
        if truyện_hiện_tại.tác_giả == MISSING_INFO:
            return []

        kết_quả_tìm_kiếm = []
        for truyện in self.danh_sách_truyện.values():
            if truyện.tên == truyện_hiện_tại.tên:
                continue

            if truyện.tác_giả.lower() == truyện_hiện_tại.tác_giả.lower():
                kết_quả_tìm_kiếm.append(truyện)
        return kết_quả_tìm_kiếm

    def gợi_ý_theo_thể_loại(self, truyện_hiện_tại: Manga):
        if truyện_hiện_tại.thể_loại == [MISSING_INFO]:
            return []

        kết_quả_tìm_kiếm = []
        for truyện in self.danh_sách_truyện.values():
            if truyện.tên == truyện_hiện_tại.tên:
                continue

            for thể_loại in truyện_hiện_tại.thể_loại:
                if thể_loại in truyện.thể_loại:
                    kết_quả_tìm_kiếm.append(truyện)
                    break
        return kết_quả_tìm_kiếm

    def update(self):
        folders = os.listdir('truyện')
        danh_sách_truyện = []
        for tên_folder in folders:
            manga = Manga(tên_folder)
            danh_sách_truyện.append(manga)
        danh_sách_truyện = sorted(
            danh_sách_truyện, key=lambda manga: manga.điểm, reverse=True
        )
        self.danh_sách_truyện = {}
        for manga in danh_sách_truyện:
            self.danh_sách_truyện[manga.tên_folder] = manga
