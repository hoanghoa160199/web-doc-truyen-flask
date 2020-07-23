import os
from datetime import datetime

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_login import LoginManager, current_user, login_user, logout_user

from controllers import CommentManager, MangaManager, UserManager
from models import Manga
from utils import Utilities as UTIL

logs = []

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

LOGIN_MANAGER = LoginManager(app)
USER_MANAGER = UserManager()
MANGA_MANAGER = MangaManager()
COMMENT_MANAGER = CommentManager()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


@LOGIN_MANAGER.user_loader
def load_user(user_id):
    return USER_MANAGER.users.get(user_id)


@app.route('/register', methods=['POST', 'GET'])
def register():
    error, success = '', ''
    if request.method == 'POST':
        name, password = request.form['username'], request.form['password']
        if USER_MANAGER.check_exist(name):
            error = "đã tồn tại"
        else:
            user = USER_MANAGER.register(name, password)
            success = "Đăng ký thành công"

        logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {success}{error}")

    send_from_directory(
        os.path.join(app.root_path, 'static'),
        'đăng_ký_thành_công.gif', mimetype='image/vnd.microsoft.gif'
    )
    return render_template('đăng_ký.html', error=error, success=success, logs=logs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error, success = None, None
    user = current_user
    if request.method == 'POST':
        name, password = request.form['username'], request.form['password']
        user = USER_MANAGER.check(name, password)
        if user:
            success = "Đăng nhập thành công"
            logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {success}")
            login_user(user)
            return redirect(url_for('trang_chủ'))
        else:
            error = 'Sai tài khoản / mật khẩu.'
            logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {error}")
    return render_template('đăng_ký.html', error=error, success=success, logs=logs, user=user)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if not current_user.is_authenticated:
        return
    logout_user()
    return redirect(url_for('trang_chủ'))


@app.route('/add_vao_tu_truyen', methods=['POST', 'GET'])
def thêm_hoặc_xóa_vào_tủ_truyện():
    # lấy các data được truyền từ frontend.
    user_id = request.args['user_id']
    ten_folder = request.args['ten_folder']
    trang_hien_tai = request.args.get('trang_hien_tai', None)

    # tìm user với user_id truyền từ frontend.
    user = USER_MANAGER.users[user_id]
    if ten_folder in user.tu_truyen:
        # xóa nếu đã có
        user.tu_truyen.remove(ten_folder)
    else:
        # thêm nếu chưa có
        user.tu_truyen.append(ten_folder)

    # cập nhật lại database
    USER_MANAGER.update_database()

    # return redirect(trang_hien_tai or url_for('trang_chủ'))
    if trang_hien_tai is None:
        return redirect(url_for('trang_chủ'))
    else:
        return redirect(trang_hien_tai)


@app.route('/xoa_khoi_tu_truyen', methods=['POST', 'GET'])
def xóa_khỏi_tủ_truyện():
    user_id = request.args['user_id']
    ten_folder = request.args['ten_folder']
    user = USER_MANAGER.users[user_id]
    user.tu_truyen.remove(ten_folder)
    USER_MANAGER.update_database()
    return redirect(url_for('trang_chủ_user'))


@app.route('/last_read', methods=['POST', 'GET'])
def last_read():
    if not current_user.is_authenticated:
        return
    ten_folder, chuong = list(current_user.last_read.items())[-1]
    return redirect(url_for('đọc_chương', ten_folder=ten_folder, chuong=chuong))


@app.route('/')
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
    ds = UTIL.phân_thành_cột(danh_sách_truyện, số_cột=4)
    return render_template('trang_chủ.html', danh_sách_truyện=ds, MANGA_MANAGER=MANGA_MANAGER)


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
    ds = UTIL.phân_thành_cột(danh_sách_truyện, số_cột=4)
    return render_template(
        'trang_chu_user.html', danh_sách_truyện=ds,
        comments=COMMENT_MANAGER.tìm_bình_luận_theo_user(current_user.id)
    )


@app.route('/doc/<ten_folder>', methods=['GET', 'POST'])
def đọc(ten_folder: str):
    truyen: Manga = MANGA_MANAGER.danh_sách_truyện[ten_folder]
    danh_sách_chương = truyen.chương.values()
    if request.method == 'POST':
        if request.form['tim_chuong'] in truyen.chương:
            danh_sách_chương = [truyen.chương[request.form['tim_chuong']]]
        elif request.form['tim_chuong'] != '':
            danh_sách_chương = []

    truyện_gợi_ý = MANGA_MANAGER.gợi_ý_theo_tác_giả(truyen)
    truyện_gợi_ý_tl = MANGA_MANAGER.gợi_ý_theo_thể_loại(truyen)

    danh_sách_chương = [c.name for c in danh_sách_chương]
    dstl = UTIL.phân_thành_cột(truyện_gợi_ý_tl, số_cột=7)
    dsgy = UTIL.phân_thành_cột(truyện_gợi_ý, số_cột=7)
    ds = UTIL.phân_thành_cột(danh_sách_chương, số_cột=11)
    return render_template(
        'chapters.html',
        truyện=truyen, danh_sách_chương=ds, truyện_gợi_ý=dsgy, truyện_gợi_ý_tl=dstl,
        comments=COMMENT_MANAGER.tìm_bình_luận_theo_truyện(ten_folder)
    )


@app.route('/doc/<ten_folder>/<chuong>', methods=['GET', 'POST'])
def đọc_chương(ten_folder: str, chuong: str):
    truyen: Manga = MANGA_MANAGER.danh_sách_truyện[ten_folder]
    try:
        danh_sách_chap = truyen.tìm_trang(chuong)
    except KeyError:
        return redirect(url_for('đọc_chương', ten_folder=ten_folder, chuong=1))

    if current_user.is_authenticated:
        current_user.last_read.pop(ten_folder, None)
        current_user.last_read[ten_folder] = chuong
        USER_MANAGER.update_database()

    ds = [[n] for n in danh_sách_chap]
    return render_template('readchap.html', truyện=truyen, chương=chuong, danh_sách_chap=ds)


@app.route('/add_comment', methods=['POST'])
def thêm_bình_luận():
    if not current_user.is_authenticated:
        return

    if request.method == 'POST':
        COMMENT_MANAGER.thêm_bình_luận(current_user.id, request.args['ten_folder'], request.form['content'])
        return redirect(url_for('đọc', ten_folder=request.args['ten_folder']))


@app.route('/uploads/<path:filename>')
def lấy_ảnh(filename):
    """Gửi ảnh lên cho Frontend để render."""
    return send_from_directory('truyện/', filename, as_attachment=True)


@app.route('/uploads/avatars/<path:user_id>')
def lấy_avatar(user_id):
    """Gửi ảnh avatar lên cho Frontend để render."""
    return send_from_directory('images/avatars/', USER_MANAGER.users[user_id].avatar, as_attachment=True)
