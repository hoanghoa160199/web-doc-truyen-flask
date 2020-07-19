class Utilities:
    @staticmethod
    def phân_thành_cột(ds, số_cột: int = 4):
        return [ds[i:i + số_cột]for i in range(0, len(ds), số_cột)]
