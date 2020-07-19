import logging
import os
import sys
from datetime import datetime
import coloredlogs
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_login import LoginManager, current_user, login_user
from forms import LoginForm
from models import Manga, MangaManager, User, UserManager

coloredlogs.DEFAULT_LEVEL_STYLES = {
    **coloredlogs.DEFAULT_LEVEL_STYLES,
    "critical": {"background": "red"},
    "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"]
}

log_level = logging.INFO
format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

coloredlogs.DEFAULT_LOG_LEVEL = log_level
coloredlogs.DEFAULT_LOG_FORMAT = format_string
coloredlogs.install(stream=sys.stdout)

logging.basicConfig(level=log_level, format=format_string)

logs = []

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
quản_lý_login = LoginManager(app)


USER_MANAGER = UserManager()
MANGA_MANAGER = MangaManager()


@quản_lý_login.user_loader
def load_user(user_id):
    return USER_MANAGER.users[user_id]


@app.route('/')
def hello_world():
    # return redirect(url_for('login'))
    return redirect(url_for('trang_chủ'))


@app.route('/register', methods=['POST'])
def register():
    error, success = '', ''
    if request.method == 'POST':

        name, password = request.form['username'], request.form['password']
        if USER_MANAGER.check_exist(name):
            error = "đã tồn tại"
        else:
            user = USER_MANAGER.register(name, password)
            success = f"Đăng ký thành công - {user}"

        logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {success}{error}")

    # return redirect(url_for('login'))
    return render_template('login.html', error=error, success=success, logs=logs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error, success = None, None
    user = current_user
    if request.method == 'POST':
        name, password = request.form['username'], request.form['password']
        user = USER_MANAGER.check(name, password)
        if user:
            success = f"Đăng nhập thành công - {user}"
            logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {success}")
            login_user(user)
            return redirect(url_for('trang_chủ'))
        else:
            error = 'Sai tài khoản / mật khẩu.'
            logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {error}")

        # return redirect(url_for('home'))
    return render_template('login.html', error=error, success=success, logs=logs, user=user)


@app.route('/add_vao_tu_truyen/<user_id>/<ten_folder>', methods=['POST', 'GET'])
def thêm_vào_tủ_truyện(user_id, ten_folder):
    user = USER_MANAGER.users[user_id]
    if ten_folder in user.tu_truyen:
        user.tu_truyen.remove(ten_folder)
    else:
        user.tu_truyen.append(ten_folder)
    USER_MANAGER.update_database()
    return redirect(url_for('trang_chủ'))


@app.route('/xoa_khoi_tu_truyen/<user_id>/<ten_folder>', methods=['POST', 'GET'])
def xóa_khỏi_tủ_truyện(user_id, ten_folder):
    user = USER_MANAGER.users[user_id]
    user.tu_truyen.remove(ten_folder)
    USER_MANAGER.update_database()
    return redirect(url_for('trang_chủ_user'))


@app.route('/trang_chu', methods=['GET', 'POST'])
def trang_chủ():
    MANGA_MANAGER.update()
    danh_sách_truyện = list(MANGA_MANAGER.danh_sách_truyện.values())
    # kiem tra method la gi
    if request.method == 'POST':  # neu method la post thi filter danh sach truyen
        # kiem tra ki tu trong from tim kiem gui ve back-end xuat hien trong ten truyen nao trong data
        if request.form['tim'] != "":
            danh_sách_truyện = MANGA_MANAGER.tìm_truyện(request.form['tim'])
        else:
            danh_sách_truyện = MANGA_MANAGER.tìm_thể_loại(request.form['tim_the_loai'])
    ds = [danh_sách_truyện[i:i+4]for i in range(0, len(danh_sách_truyện), 4)]
    return render_template('trang_chủ.html', danh_sách_truyện=ds)


@app.route('/trang_chu_user', methods=['GET', 'POST'])
def trang_chủ_user():
    if not current_user.is_authenticated:
        return redirect(url_for('trang_chủ'))
    MANGA_MANAGER.update()
    danh_sách_truyện = []
    for ten_folder in current_user.tu_truyen:
        manga = MANGA_MANAGER.danh_sách_truyện[ten_folder]
        danh_sách_truyện.append(manga)
    if request.method == 'POST':
        if request.form['tim'] != "":
            danh_sách_truyện = MANGA_MANAGER.tìm_truyện(request.form['tim'])
        else:
            danh_sách_truyện = MANGA_MANAGER.tìm_thể_loại(request.form['tim_the_loai'])
    ds = [danh_sách_truyện[i:i+4]for i in range(0, len(danh_sách_truyện), 4)]
    return render_template('trang_chu_user.html', danh_sách_truyện=ds)


@app.route('/doc/<ten_folder>', methods=['GET', 'POST'])
def đọc(ten_folder: str):
    truyen: Manga = MANGA_MANAGER.danh_sách_truyện[ten_folder]
    danh_sách_chương = truyen.chương.values()
    if request.method == 'POST':
        if request.form['tim_chuong'] in truyen.chương:
            danh_sách_chương = [truyen.chương[request.form['tim_chuong']]]
        elif request.form['tim_chuong'] != '':
            danh_sách_chương = []
    truyện_gợi_ý = []
    truyện_gợi_ý_tl = []

    for truyen_goi_y in MANGA_MANAGER.danh_sách_truyện.values():
        if truyen.tác_giả.lower() == truyen_goi_y.tác_giả.lower() and truyen.tên != truyen_goi_y.tên:
            truyện_gợi_ý.append(truyen_goi_y)
        for the_loai in truyen.thể_loại:
            if the_loai in truyen_goi_y.thể_loại:
                truyện_gợi_ý_tl.append(truyen_goi_y)
                break

    danh_sách_chương = [c.name for c in danh_sách_chương]
    dstl = [truyện_gợi_ý_tl[i:i+7]for i in range(0, len(truyện_gợi_ý_tl), 7)]

    dsgy = [truyện_gợi_ý[i:i+7]for i in range(0, len(truyện_gợi_ý), 7)]
    ds = [danh_sách_chương[i:i+4]for i in range(0, len(danh_sách_chương), 4)]
    return render_template('chapters.html', truyện=truyen, danh_sách_chương=ds, truyện_gợi_ý=dsgy, truyện_gợi_ý_tl=dstl)


@app.route('/doc/<ten_folder>/<chuong>', methods=['GET', 'POST'])
def đọc_chương(ten_folder: str, chuong: str):
    truyen: Manga = MANGA_MANAGER.danh_sách_truyện[ten_folder]
    try:
        danh_sách_chap = truyen.tìm_trang(chuong)
    except KeyError:
        return redirect(url_for('đọc_chương', ten_folder=ten_folder, chuong=1))

    ds = [[n] for n in danh_sách_chap]
    return render_template('readchap.html', truyện=truyen, chương=chuong, danh_sách_chap=ds)


@app.route('/uploads/<path:filename>')
def lấy_ảnh(filename):
    """Gửi ảnh lên cho Frontend để render."""
    return send_from_directory('truyện/', filename, as_attachment=True)
