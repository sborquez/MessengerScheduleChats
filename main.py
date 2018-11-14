# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 22:36:34 2018

@author: sebas
"""
#%%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from tinydb import TinyDB, Query
from tinydb.operations import delete, add

import getpass
from os import path
import sys

from time import strptime, strftime, localtime

webdriver_path = sys.argv[1] if len(sys.argv) == 3 else "C:/Users/sebas/Projects/Developing/MessengerScheduleChats/webdriver/chromedriver.exe"
schedule_db_path = sys.argv[2] if len(sys.argv) == 3 else "C:/Users/sebas/Projects/Developing/MessengerScheduleChats/schedule.json"

DEBUG = True
_email = ""

date_format = "%y-%m-%d %H:%M"

def is_logged(driver):
    return driver.current_url != "https://www.messenger.com/"

def get_login_credentials():
    _email = input("email: ")
    _password = getpass.getpass("password: ")
    return _email, _password
    
def loggin(driver):
    global _email
    _email, _password = get_login_credentials()
    driver.find_element_by_id("email").send_keys(_email)
    driver.find_element_by_id("pass").send_keys(_password)
    driver.find_element_by_id("loginbutton").click()
    
def logout():
    #TODO
    pass

def send_msg(msg):
    #TODO
    pass

#%%
def get_database(email):
    db = TinyDB(schedule_db_path)


    # {"email":<email>, [ {"nick":<nick>, "name": <name>, "face_url":<face_url>}, ...]}
    contacts_db = db.table("contacts")
    if len(contacts_db.search(Query()["email"] == email)) == 0:
        contacts_db.insert({"email":email, "chats":[]})
    # {"email":<email>,
    #   "sent": [{"to":<name>|<nick>, "content":<text>, "reminder":{"date":<dd-mm-yy>, "time": <HH:MM>}}}]
    #   "outbox":[{"to":<name>|<nick>, "content":<text>, "reminder":{"date":<dd-mm-yy>, "time": <HH:MM>}}}, ...]
    #   "week": [{"to":<name>|<nick>, "content":<text>, "reminder":{"days":[<1-7>], "time": [<HH:MM>], "total_sent": 0 }}] 
    # }
    messages_db = db.table("messages")
    if len(messages_db.search(Query()["email"] == email)) == 0:
        messages_db.insert({"email":email, "sent": [], "outbox":[], "week":[]})
    return contacts_db, messages_db

def get_contacts(email, contacts_db):
    return contacts_db.search(Query()["email"] == email)

def get_contact(email, name, contacts_db):
    contacts = contacts_db.search(Query()["email"] == email)
    for contact in contacts["chats"]:
        if contact["name"] == name or contact["nick"] == name:
            return dict(contact)

def add_to_outbox(email, to, content, date, time, messages_db):
    if type(date) != str or type(time) != str:
        raise TypeError("Must use str formats")
    new_message = {"to":to, "content":content, "reminder":{"date":date, "time":time}}
    
    outbox = messages_db.get(Query()['email'] == email)["outbox"] + [new_message]
    outbox = sorted(outbox, key=lambda msg: strptime(f"{msg['reminder']['date']} {msg['reminder']['time']}", date_format))
    
    return messages_db.update({"outbox" : outbox}, Query()["email"] == email)

def del_msg_outbox(messages_db):
    #TODO
    pass

def check_and_send_outbox(email, messages_db):
    
    outbox = messages_db.get(Query()["email"] == email)["outbox"]
    now = localtime()
    
    msgs_sent = 0
    for msg in outbox:
        send_date =  strptime(f"{msg['reminder']['date']} {msg['reminder']['time']}", date_format)
        if now < send_date:
            break
        msgs_sent += 1
        send_msg(msg)
        
    if msgs_sent:
        messages_db.update(add("sent", outbox[:msgs_sent]), Query()["email"] == email)
        messages_db.update({"outbox" : outbox[msgs_sent:] }, Query()["email"] == email)

    return msgs_sent
            

#%%
def main():
    driver = webdriver.Chrome(webdriver_path)
    driver.get("https://www.messenger.com")

    if is_logged(driver) and not DEBUG:
        # TODO cerrar sesion  
        print("closing previous session")
        logout()

    # Try to log in
    loggin()
    while driver.current_url == "https://www.messenger.com/login/password/":
        print("email or password is incorrect. Try again.")
        loggin()
    contacts_db, messages_db = get_database(_email)    

    driver.close()
    
#%%
#main()

#%%
if __name__ == "__main__":
    main()