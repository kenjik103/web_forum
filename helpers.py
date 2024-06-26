import sqlite3

import csv
import datetime
from typing import Any
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps

from random import randint
from datetime import datetime

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def class_code_generator(user_id):
    """ Generates unique class id based off user_id"""
    i = user_id
    num_places = 1
    while i > 0:
        i //= 10
        num_places *= 10
        
    random_integer = randint(1000, 9999)
    return random_integer * num_places + user_id

def get_datetime():
    """ returns date and time as a tuple(date, time)"""
    now = datetime.now()
    return (now.strftime("%m/%d/%Y"), now.strftime("%H:%M:%S"))
    

class DataBase:
    def __init__(self, file_path):
        conn = sqlite3.connect(file_path, check_same_thread=False)
        self.conn = conn

    def select_from_db(self, command):
        cur = self.conn.cursor()
        cur.execute(command)

        rows = cur.fetchall()
        return rows
    
    def select_priority_from_db(self, command, priority):
        cur = self.conn.cursor()
        cur.execute(command, priority)
        rows = cur.fetchall()
        return rows

    def insert_into_db(self, command, task):
        cur = self.conn.cursor()
        cur.execute(command, task)
        self.conn.commit()

    def delete_from_db(self, command, priority):
        cur = self.conn.cursor()
        cur.execute(command, priority)
        self.conn.commit()
