import logging
import os
import pathlib
import sys
from datetime import datetime
from itertools import zip_longest

import coloredlogs
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_caching import Cache

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

CACHE = Cache(app)

USER_MANAGER = UserManager()
MANGA_MANAGER = MangaManager()


@app.route('/')
def hello_world():
    # return redirect(url_for('login'))
    return redirect(url_for('trang_chủ'))


@app.route('/register', methods=['POST'])
def register():
    error, success = None, None
    if request.method == 'POST':
        name, password = request.form['username'], request.form['password']
        user = USER_MANAGER.register(name, password)
        success = f"Đăng ký thành công - {user}"
        CACHE.set('user_id', user.id)
        logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {success}")

    return redirect(url_for('login'))
    # return render_template('login.html', error=error, success=success, logs=logs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (user_id := CACHE.get('user_id')):
        user = USER_MANAGER.users[user_id].to_dict()
    else:
        user = {}

    error, success = None, None
    if request.method == 'POST':
        name, password = request.form['username'], request.form['password']
        user = USER_MANAGER.check(name, password)
        if user:
            success = f"Đăng nhập thành công - {user}"
            CACHE.set('user_id', user.id)
            user = {}
            logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {success}")
        else:
            error = 'Sai tài khoản / mật khẩu.'
            logs.append(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {error}")
            user = {}

        # return redirect(url_for('home'))
    return render_template('login.html', error=error, success=success, logs=logs, user=user)


@app.route('/trang-chu', methods=['GET', 'POST'])
def trang_chủ():
    MANGA_MANAGER.update()
    danh_sách_truyện = list(MANGA_MANAGER.danh_sách_truyện.values())
    # kiem tra method la gi
    if request.method == 'POST':  # neu method la post thi filter danh sach truyen
        # kiem tra ki tu trong from tim kiem gui ve back-end xuat hien trong ten truyen nao trong data
        danh_sách_truyện = MANGA_MANAGER.tìm_truyện(request.form['tim'])

    ds = zip_longest(
        danh_sách_truyện[0::4], danh_sách_truyện[1::4],
        danh_sách_truyện[2::4], danh_sách_truyện[3::4]
    )

    return render_template('trang_chủ.html', danh_sách_truyện=ds)

# @app.route('/truyện',methods)
@app.route('/doc/<ten_folder>', methods=['GET', 'POST'])
def đọc(ten_folder: str):
    truyen: Manga = MANGA_MANAGER.danh_sách_truyện[ten_folder]
    danh_sách_chương = truyen.chương.values()
    if request.method == 'POST':
        if request.form['tim_chuong'] in truyen.chương:
            danh_sách_chương = [truyen.chương[request.form['tim_chuong']]]
        elif request.form['tim_chuong'] != '':
            danh_sách_chương = []

    danh_sách_chương = [c.name for c in danh_sách_chương]

    ds = zip_longest(danh_sách_chương[::4], danh_sách_chương[1::4], danh_sách_chương[2::4], danh_sách_chương[3::4])
    return render_template('chapters.html', truyện=truyen, danh_sách_chương=ds)


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
