from ast import Index
from asyncio import events
from calendar import c
from genericpath import exists
from json import load
from msilib.schema import Property
from optparse import Values
import sqlite3
from config import *
from urls import *
from functions import *
import time
import os
from cryptography.fernet import Fernet
from os import getcwd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium import webdriver
import pyautogui as pygui
import re

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.properties import Clock
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.uix.dropdown import DropDown

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '900')


class Database():
    "This class has basic info about your account"
    def __init__(self, dbase_path) -> None:
        self.con = sqlite3.connect(dbase_path)   #dir_dbase
        self.c = self.con.cursor()


    def __del__(self):
        self.con.close()


    def create_new_account(self, id, username, password) -> None:       #ta metoda w gui
        entry = self.fetchall_record(columns='*', table='Accounts', conditions={'acc_id': id})

        if not entry:
            encrypted_password = self._encrypt_password(id, password)
            self.insert_record('Accounts', values=[id, username, encrypted_password])
        else:
            print(f'Account with id: {id} already exists!')
    

    def load_account_data(self, id : int) -> None:
        data = self.fetchall_record(columns=['login', 'password'], table='Accounts', conditions={'acc_id': id})
        username, encrypted_password = data[0]
        password = self._decrypt_password(id, encrypted_password)

        return username, password


    def insert_record(self, table : str, values : list) -> None:
        self.c.execute(f'''INSERT OR IGNORE INTO {table}
                        VALUES({','.join(['?' for _ in values])})''', values)
        self.con.commit()


    def fetchall_record(self, columns : list, table : str, conditions : dict) -> list:
        values = conditions.values()
        self.c.execute(f'''SELECT {', '.join([f'{column}' for column in columns])}
                        FROM {table}
                        WHERE {' and '.join([f'{condition}=?' for condition in conditions])}''',
                        tuple(values))
     
        return self.c.fetchall()


    def delete_record(self, table: str, conditions : dict) -> None:   #zrobic usuwanie + powiadomienie ze zostana wszystkie inne info nt przedmiotow usuniete
        values = conditions.values()
        self.c.execute(f'''DELETE FROM {table}
                        WHERE {' AND '.join([f'{condition}=?' for condition in conditions])}''',
                        tuple(values))
        self.con.commit()
        
    
    
    def delete_account(self, id : int, input_password : str) -> None: #hasło musi być poprawne żeby usunać konto z bazy!

        username, password = self.load_account_data(id)
        if input_password == password:
            self.delete_record(table='Accounts', conditions={'acc_id' : id})

            path = getcwd()
            dir_mykey = path + f'\\mykey_{str(id)}'
            try:
                os.remove(dir_mykey)
            except:
                print('File not found!')

        else:
            print('Wrong password!')


    def _encrypt_password(self, id, password) -> None:
        key = Fernet.generate_key()

        with open(f'mykey_{str(id)}', 'wb') as mykey:
            mykey.write(key)
        print(f'mykey_{str(id)}')

        f = Fernet(key)
        return f.encrypt(password.encode())
       

    def _decrypt_password(self, id, encrypted_password) -> None:
        path = getcwd()
        dir_mykey = path + f'\\mykey_{str(id)}'

        with open(dir_mykey, 'rb') as mykey:
            key = mykey.read()

        f = Fernet(key)
        return f.decrypt(encrypted_password).decode("utf-8")

db = Database()



    


Screens
class MainWindow(Screen):
    target = ObjectProperty()
    number_of_acc = len(db.accounts_list)
    event_list = []
    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_interval(self.update, 1/60)


    def update(self, dt):
        
        if self.manager.current == 'accounts':
            MyAccountsWindow.load_accounts(self)

        if self.manager.current == 'login':
            self.manager.get_screen(self.manager.current).ids.spinner_id.values = db.accounts_list
        
        if self.manager.current == 'add_new_account':
            # AddAccountWindow.input_checker()
            pass




            # username_inp = self.manager.get_screen(self.manager.current).ids.username_input.text
            # password_inp = self.manager.get_screen(self.manager.current).ids.password_input.text
            # acc_id_inp = self.manager.get_screen(self.manager.current).ids.account_id_input.text

            # if (username_inp and password_inp and acc_id_inp) != '':
            #     AddAccountWindow.st(self)
            #     app = VintedApp.get_running_app()
            #     add_screen = app.root.get_screen('add_new_account')

            #     bl = add_screen.sumbit_enabled
            #     print(bl)

            # print(username_inp)
            # print(password_inp)
            # print(acc_id_inp)
            pass
            #zrobic to moze na ekranie funckje i tu wywolac


                



class LoginInWindow(Screen):
    acc_list = ListProperty(None)
    
    def __init__(self, **kw):
        super().__init__(**kw)


    def spinner_clicked(self, value):
        self.ids.click_label.text = f'You selected:{value}'



class MyAccountsWindow(Screen):
    # acc1 = ObjectProperty(None)
    # acc2 = ObjectProperty(None)
    # acc3 = ObjectProperty(None)
    # acc4 = ObjectProperty(None)
    # acc5 = ObjectProperty(None)
    def on_reload(self):
        db.create_new_account()


    def load_accounts(self, *args):
        # print('dzziala')
        obj = self.manager.get_screen(self.manager.current).ids
    
        if self.number_of_acc != len(db.accounts_list):
            db.load_accounts()
            self.number_of_acc = len(db.accounts_list)

        for i in range(5):
            try:
                obj[f'acc{str(i+1)}'].text = db.accounts_list[i]+' - press to show more info'
        
            except IndexError:
                obj[f'acc{str(i+1)}'].text = 'Empty!'


class AppSettingsWindow(Screen):
    pass

class AddAccountWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    acc_id = ObjectProperty(None)

    sumbit_enabled = BooleanProperty(False)

    def st(self):
        # print('dziala')
        self.sumbit_enabled = True
    
    def on_click_add_btn(self):
        print(self.ids.username_input.text, self.ids.password_input.text, self.ids.account_id_input.text)

    def clear_inputs_fields(self):
        self.account_id_input.text = ''
        self.password_input.text = ''
        self.username_input.text = ''

    def input_checker(self, *args):
        pass
        # obj = self.manager.get_screen(self.manager.current).ids
        # print(obj)


        


        # name = obj['username_input'].text
        # psw = obj['password_input'].text
        # id = obj['account_id_input'].text

        # print(name, psw, id)
        # if (name and psw and id) == '':
        #     AddAccountWindow.sumbit_enabled = True
        # # print(obj['username_input'].text)
        # # print(self.username_input)





#screen manager
class WindowManager(ScreenManager):
    pass



class AccountPrinterLayout(StackLayout):
    pass






kv = Builder.load_file("vinted.kv")


class VintedApp(App):
    def build(self):
        return kv
    

if __name__ == "__main__":
    VintedApp().run()
