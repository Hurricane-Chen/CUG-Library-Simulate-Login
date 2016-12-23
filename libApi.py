# !/usr/bin/python3
# coding=utf-8
import cuglib
import time
import datetime
import logging
from flask import Flask
from flask import jsonify
from flask import request
from cuglib import LibUser


app = Flask(__name__)
user_list = []

# user_list 用于存储大约5min内登录过的LibUser
# 每当有新的查询请求时会触发删除5min内未登录的LibUser


class UserAndTime(object):
    def __init__(self, user):
        self.user = user
        self.add_time = time.time()


def get_stored_user(userid):
    now_time = time.time()
    while len(user_list) > 0:
        if now_time - user_list[0].add_time > 300:
            user_list.pop(0)
        else:
            break
    for i in user_list:
        if i.user.userid == userid:
            return i.user
    return None


def make_log(log_type):
    logger = logging.getLogger('mylogger' + str(time.time()))
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
    fh = logging.FileHandler('./log/' + log_type + '-' + str(datetime.date.today()) + '.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


@app.route('/VerifyPassword', methods=['POST'])
def verify():
    # 验证用户图书馆登录密码
    logger = make_log('verify')
    userid = request.form.get('userid', default='0')
    password = request.form.get('password', default=userid)
    if len(userid) != 11:
        message = userid + " Length of userid is not 11"
        logger.debug(message)
        return jsonify(result=0, reason="学号长度不正确")
    try:  # 测试能否成功 否则raise一个cuglib中的登录异常并获取信息
        temp = LibUser(userid, password)
        return jsonify(result=1)
    except cuglib.LibLoginException as info:
        if info.response == "对不起，密码错误，请查实！":
            message = userid + " Wrong password"
            logger.info(message)
            return jsonify(result=0, reason="密码错误")
        else:
            message = userid + "unknown error: " + info.response
            logger.error(message)
            return jsonify(result=0, reason="未知错误")
    message = "Unknow error without information"
    logger.error(message)
    return jsonify(result=0, reason="未知错误")


@app.route('/GetNowBooks', methods=['POST'])
def get_books():
    # 获取当前借阅书籍
    logger = make_log('get_books')
    userid = request.form.get('userid', default='0')
    password = request.form.get('password', default=userid)
    temp = get_stored_user(userid)
    if temp is None:
        try:
            temp = LibUser(userid, password)
            user_list.append(UserAndTime(temp))
        except:
            logger.debug(userid + ' Unable to login when search books')
            return jsonify(result=0, reason="无法登录")
    return jsonify(result=1, list=cuglib.now(temp))


@app.route('/GetHistoryBooks', methods=['POST'])
def get_history():
    # 获取历史借阅书籍
    logger = make_log('get_history')
    userid = request.form.get('userid', default='0')
    password = request.form.get('password', default=userid)
    temp = get_stored_user(userid)
    if temp is None:
        try:
            temp = LibUser(userid, password)
            user_list.append(UserAndTime(temp))
        except:
            logger.debug(userid + ' Unable to login when search history')
            return jsonify(result=0, reason="无法登录")
    return jsonify(result=1, list=cuglib.history(temp))


@app.route('/RebookAll', methods=['POST'])
def rebook_all():
    # 续借所有书籍
    logger = make_log('rebook')
    userid = request.form.get('userid', default='0')
    password = request.form.get('password', default=userid)
    temp = get_stored_user(userid)
    if temp is None:
        try:
            temp = LibUser(userid, password)
            user_list.append(UserAndTime(temp))
        except:
            logger.debug(userid + ' Unable to login when search history')
            return jsonify(result=0, reason="无法登录")
    failure = temp.all_rebook()  # 返回借阅失败的书籍名称
    if len(failure) == 0:
        return jsonify(result=1)
    else:
        return jsonify(result=0, failure=failure)


@app.route('/RebookSingle', methods=['POST'])
def rebook_single():
    logger = make_log('rebook')
    userid = request.form.get('userid', default=0)
    password = request.form.get('password')
    bar_code = request.form.get('barcode')
    temp = get_stored_user(userid)
    if temp is None:
        try:
            temp = LibUser(userid, password)
            user_list.append(UserAndTime(temp))
        except:
            logger.debug(userid + ' Unable to login when search history')
            return jsonify(result=0, reason="无法登录")
    try:
        if temp.single_rebook(bar_code):
            return jsonify(result=1)
        else:
            return jsonify(result=0)
    except cuglib.RebookException as info:
        return jsonify(result=0, reason=info.information)


@app.route('/GetArrears', methods=['POST'])
def get_arrears():
    logger = make_log('arrears')
    userid = request.form.get('userid', default=0)
    password = request.form.get('password')
    bar_code = request.form.get('barcode')
    temp = get_stored_user(userid)
    if temp is None:
        try:
            temp = LibUser(userid, password)
            user_list.append(UserAndTime(temp))
        except:
            logger.debug(userid + ' Unable to login when search history')
            return jsonify(result=0, reason="无法登录")
    info = temp.arrears()
    return jsonify(result=1, info=info)


if __name__ == "__main__":
    app.run('127.0.0.1', debug=True, port=8000)
