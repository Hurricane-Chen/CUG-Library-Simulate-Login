#! /usr/bin/python3
# coding=utf-8


# Running this program on a unix-like operating system
# And install Tesseract on your system before running it


import requests
import os
import re
import json
from bs4 import BeautifulSoup

# Struck Request headers
agent = "Mozilla/5.0 (Windows NT 5.1; rv:49.0) Gecko/20100101 Firefox/49.0"
my_headers = {
    'User-Agent': agent,
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive'
}


class LibLoginException(Exception):
    # LibLoginException is for situation that logging in failure
    def __init__(self, response):
        self.response = response


class RebookException(Exception):
    # RebookException is for situation that rebook failure
    def __init__(self, information):
        self.information = information


class Book(object):
    # Attention: argument 'check' is a query string for rebook
    # Sign it if you want to use method 'rebook'
    def __init__(self, name, bar_code, book_date, return_date, check=None):
        self.name = name
        self.bar_code = bar_code
        self.book_date = book_date
        self.return_date = return_date
        self.check = check

    def dict_convert(self):
        book_dict = {
            "书名": self.name,
            "条码号": self.bar_code,
            "借阅日期": self.book_date,
            "归还日期": self.return_date
        }
        return book_dict


class LibUser(object):
    def __init__(self, userid, password):
        self.session = requests.session()  # set cookie
        self.session.headers = my_headers  # set headers
        self.userid = userid
        self.password = password
        self.login()

    def read_captcha(self):
        # read captcha, both necessary for method rebook and login
        url = "http://202.114.202.207/reader/captcha.php"
        req = self.session.get(url)
        with open("captcha_test.gif", "wb") as gif:
            gif.write(req.content)
        os.system("tesseract captcha_test.gif text")  # use tesseract in command line
        with open("text.txt", "r") as t:
            text = t.readline()
        return text[0:4]

    def login(self):
        params = {
            "number": self.userid,
            "passwd": self.password,
            "select": "cert_no"
        }
        url = "http://202.114.202.207/reader/redr_verify.php"
        params["captcha"] = self.read_captcha()
        print("----User:", params["number"], "Logging in----")
        n = self.session.post(url, params)
        n.encoding = "utf-8"
        soup = BeautifulSoup(n.text, "html.parser")
        judge = soup.find("font", {"color": "red"})
        if judge is not None:  # test login success or not
            raise LibLoginException(judge.get_text())
        return

    def now_books(self):  # return a list of class books
        doc = self.session.get("http://202.114.202.207/reader/book_lst.php")
        doc.encoding = "utf-8"
        soup = BeautifulSoup(doc.text, "html.parser")
        name_list = get_souplist_text(soup.find_all("a", {"class": "blue"}))
        date_text = soup.find_all("td", {"class": "whitetext", "width": "13%"})
        date_list = []
        for date in date_text:
            date_list += re.findall("[0-9]+-[0-9]+-[0-9]+", date.get_text())
        code_list = []
        check_list = []
        code_text = soup.find_all("input", {"title": "renew", "class": "btn btn-success"})
        for code in code_text:
            code = code.get("onclick")
            bar_check = re.findall("'([^',]+)'", code)
            code_list.append(bar_check[0])
            check_list.append(bar_check[1])
        book_list = []
        index = 0
        while index < len(name_list) and 2 * index + 1 < len(date_list):
            temp = Book(name_list[index], code_list[index], date_list[2 * index],
                        date_list[2 * index + 1], check=check_list[index])
            book_list.append(temp)
            index += 1
        return book_list

    def history_books(self):
        # return a list of books you booked before
        url = 'http://202.114.202.207/reader/book_hist.php'
        info = self.session.post(url, data={'para_string': 'all'})
        info.encoding = "utf-8"
        soup = BeautifulSoup(info.text, "html.parser")
        name_list = get_souplist_text(soup.find_all("a", {"class": "blue"}))
        date_list = get_souplist_text(soup.find_all("td", {"class": "whitetext", "width": "12%"}))
        code_list = get_souplist_text(soup.find_all("td", {"class": "whitetext", "width": "10%"}))
        index = 0
        book_list = []
        while index < len(name_list):
            temp = Book(name_list[index], code_list[index],
                        date_list[2 * index], date_list[2 * index + 1])
            book_list.append(temp)
            index += 1
        return book_list

    def rebook(self, book):
        # rebook single book, only Book type argument acceptable
        url = 'http://202.114.202.207/reader/ajax_renew.php'
        params = {
            'bar_code': book.bar_code,
            'check': book.check,
            'captcha': self.read_captcha(),
            'time': '0'
        }
        info = self.session.get(url, params=params)
        info.encoding = "utf-8"
        soup = BeautifulSoup(info.text, "html.parser")
        judge = soup.find("font")
        if judge.get_text() == "续借成功":
            return
        else:
            raise RebookException(judge.get_text())

    def all_rebook(self):
        # rebook all books
        failure = []
        for book in self.now_books():
            try:
                self.rebook(book)
            except RebookException:
                failure.append(book.name)
        return failure


def get_souplist_text(souplist):
    count = 0
    while count < len(souplist):
        souplist[count] = souplist[count].get_text()
        count += 1
    return souplist


def now(user):
    book_list = user.now_books()
    i = 0
    while i < len(book_list):
        book_list[i] = book_list[i].dict_convert()
        i += 1
    return book_list


def history(user):
    history_list = user.history_books()
    i = 0
    while i < len(history_list):
        history_list[i] = history_list[i].dict_convert()
        i += 1
    return history_list


if __name__ == "__main__":
    for i in range(20151001277, 20151001278):
        try:
            x = LibUser(str(i), str(i) + 's')
        except LibLoginException as n:
            if n.response == "对不起，密码错误，请查实！":
                print(n)
            else:
                print('ss')
