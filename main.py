import os
import json
import base64
import sqlite3
from Crypto.Cipher import AES
import win32crypt
import shutil
from datetime import timezone, datetime, timedelta
from tkinter import *
import plotly.graph_objects as go


def get_chrome_datetime(chromedate):

    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)


    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    
    key = key[5:]

    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def strongPasswordChecker(s):
    SpecialSym =['~', ':', "'", '+', '[', '\\', '@', '^', '{', '%', '(', '-', '"', '*', '|', ',', '&', '<', '`', '}', '.', '_', '=', ']', '!', '>', ';', '?', '#', '$', ')', '/'] 
    i=0
    if(len(s)>0 and len(s)<=6):
        i=1
    elif len(s) > 6 and len(s)<=12:
        i=3
    elif len(s) > 12:
        i=5
    if any(char.isdigit() for char in s):
        i=i+1
    
    if any(char.isupper() for char in s): 
        i=i+1 
       
    if any(char.islower() for char in s): 
        i=i+1   
    if any(char in SpecialSym for char in s): 
        i=i+2
    return i

def decrypt_password(password, key):
    try:

        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""
