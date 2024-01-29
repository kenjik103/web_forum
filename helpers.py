import sqlite3

import csv
import datetime
from typing import Any
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps

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
        cur.execute(command, (priority,))
        rows = cur.fetchall()
        return rows

    def insert_into_db(self, command, task):
        cur = self.conn.cursor()
        cur.execute(command, task)
        self.conn.commit()