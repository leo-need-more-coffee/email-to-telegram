import datetime
import json
import random
import csv
import sqlite3
import time


def to_dict(tup):
    id, number, imap, username, password, chat_id, last_email, is_editing = tup

    d = dict({"id": id,  "number": number, "imap": imap, "username": username, "password": password, "chat_id": chat_id, "last_email": last_email, "is_editing": is_editing})
    return d


async def create_user(id, number=0, imap=None, username=None, password=None, chat_id=None, last_email=None, is_editing=False):
    conn = sqlite3.connect('data.db')
    conn.execute("INSERT INTO users (id, number, imap, username, password, chat_id, last_email, is_editing) \
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, number, imap, username, password, chat_id, last_email, is_editing))
    conn.commit()
    conn.close()


async def get_users():
    conn = sqlite3.connect('data.db')
    cursor = conn.execute("SELECT id, number, imap, username, password, chat_id, last_email, is_editing FROM users")
    rows = list([to_dict(el) for el in cursor.fetchall()])
    conn.close()
    return rows


async def get_user(id):
    conn = sqlite3.connect('data.db')
    cursor = conn.execute("SELECT id, number, imap, username, password, chat_id, last_email, is_editing FROM users WHERE id==?",
                          [id])
    rows = list([to_dict(el) for el in cursor.fetchall()])
    conn.close()
    return rows


async def get_editing_data(id):
    conn = sqlite3.connect('data.db')
    cursor = conn.execute("SELECT id, number, imap, username, password, chat_id, last_email, is_editing FROM users WHERE id == ? AND is_editing == 1",
                          (id, ))
    rows = cursor.fetchall()
    row = to_dict(rows[0])
    conn.close()
    return row


async def is_user(id):
    conn = sqlite3.connect('data.db')
    cursor = conn.execute("SELECT id, number, imap, username, password, chat_id, chat_id, last_email, is_editing FROM users WHERE id==?",
                          [id])
    rows = cursor.fetchall()
    conn.close()
    if len(rows) == 0:
        return False
    return True


async def edit_user(user):
    id, number, imap, username, password, chat_id, last_email, is_editing = user.values()
    conn = sqlite3.connect('data.db')
    conn.execute(
        "UPDATE users SET number = ?, imap = ?, username = ?, password = ?, chat_id = ?, last_email = ?, is_editing = ? WHERE id == ? AND number == ?",
        (number, imap, username, password, chat_id, last_email, is_editing, id, number, ))
    conn.commit()
    conn.close()


async def delete_user(id):
    conn = sqlite3.connect('data.db')
    conn.execute("DELETE FROM users\
            WHERE id ==?", [id])
    conn.commit()
    conn.close()

async def delete_email(id, number):
    conn = sqlite3.connect('data.db')
    conn.execute("DELETE FROM users\
            WHERE id ==? AND number ==?", [id, number])
    conn.commit()
    conn.close()