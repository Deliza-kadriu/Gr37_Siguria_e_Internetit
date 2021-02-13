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
        
def main1():
    
    arr=[]
    arr1=[]
    key = get_encryption_key()
    print(key)
    db_path = os.path.join(os.environ["USERPROFILE"],"AppData", "Local","Google", "Chrome", "User Data", "default", "Login Data")

    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    
    db = sqlite3.connect(filename)
    cursor = db.cursor()

    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    

    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]
        
        if username and password:
            if(origin_url.find('@')!=-1):
                x = origin_url.split("@")
                arr.append(x[1])
            else :
                arr.append(origin_url[0:40])
            if password:
                a=strongPasswordChecker(password)
                arr1.append(a)
            else:
                arr1.append(0)

            print(f"Origin URL: {origin_url}")
            print(f"Username: {username}")
            print(f"Password: {password}")
        else:
            continue
        if date_created != 86400000000 and date_created:
            print(f"Creation date: {str(get_chrome_datetime(date_created))}")
        if date_last_used != 86400000000 and date_last_used:
            print(f"Last Used: {str(get_chrome_datetime(date_last_used))}")
        print("="*50)

    
    fig = go.Figure([go.Bar(x=arr, y=arr1)])
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.6)
    fig.update_layout(title_text='Kompleksiteti i fjalekalimeve nga 1-10')
    fig.write_html('graph.html', auto_open=True)
    
    cursor.close()
    db.close()

    try:

        os.remove(filename)
    except:
        pass
    

def main():
    window = Tk()
    window.title("Detyra e 5 : Leximi i fjalekalimeve nga browseri")
    window.geometry("450x350")
    window['background'] = 'white'
    lbl = Label(window, text="Shtyp butonin per te pare fjalekalimet e ruajtura !" ,background = "white", font=("Arial Bold", 12)).place(x=20,y=50)
   

    button = Button(window, text='Chrome Passwords',background = "#66CDAA",activebackground = "#66CDAA",border=0.5, width=15,
    height=3, command=main1).place(x=160, y=100)
    
    window.mainloop()
if __name__ == "__main__":
    main()
