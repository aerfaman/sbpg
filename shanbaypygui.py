import tkinter as tk
from tkinter import *
from getToken import getToken
from getuserinfo import getuserinfo
from searchandadd import searchandadd
import sqlite3
from tkinter import messagebox
import os
import logging
import json

with open('config.json','r') as f:
    data=json.load(f)


LARGE_FONT= ("Verdana", 12)
appkey="053f752df750407cd292"
currentPath=os.getcwd()




databaseStatus={"status":0}

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)-4s %(message)s',
                datefmt='%m-%d %H:%M',
                filename='sbpg.log',
                filemode='w')
logging.info("Opened sbpg")
logging.info("Create or connect database")

try:
    logging.info('Getting configs from config.json file')
    with open('config.json','r') as f:
        data=json.load(f)
    appkey=data['apisettings']['apikey']
except Exception as e:
    logging.error("Can not get config ,Please check config.json file")
    logging.error('----%s'%e)




try:
    conn = sqlite3.connect(r'%s\sbpg.db'%currentPath)
    c = conn.cursor()
    logging.info("Connected to database")
except Exception as e:
    logging.error("Connect to database failed:")
    logging.error('----%s'%e)
    databaseStatus['status']=1
    databaseStatus['message']="Connect to database failed ,Please goto log file get more ditail"

logging.info("Checking Tables status")
try:
    sqlCreateTable='CREATE TABLE IF NOT EXISTS apitoken (`rowid`,`apitoken` VARCHAR(100) NOT NULL, `username` VARCHAR(32) NOT NULL, `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);'
    c.execute(sqlCreateTable)
    sqlCreateTable='CREATE TABLE IF NOT EXISTS apitokenusing ( `apitoken` VARCHAR(100) NOT NULL);'
    c.execute(sqlCreateTable)
    sqlCreateTable='CREATE TABLE IF NOT EXISTS searchhistory ( `rowid`,`word` VARCHAR(100) NOT NULL,`shanbayid` VARCHAR(32),`definition` VARCHAR(100) NOT NULL,`ukpcs` VARCHAR(30),`uspcs` VARCHAR(30) );'
    c.execute(sqlCreateTable)
    conn.commit()
    logging.info("Table exist")
except Exception as e:
    logging.error("Create Table failed:")
    logging.error("----%s"%e)
    databaseStatus['status']=1
    databaseStatus['message']="Connect to database failed ,Please goto log file get more ditail"



def checkTokenStatus():
    apitoken=""
    tokenStatus={}
    try:
        c = conn.cursor()
        sqlSelectApiToken='SELECT apitoken from apitokenusing;'
        sqlApiToken=c.execute(sqlSelectApiToken)
        apitoken=sqlApiToken.fetchone()[0]
    except Exception as e:
        tokenStatus['status']=1
        tokenStatus['message']='select sql excecute failed'
        return tokenStatus
    gu=getuserinfo(apitoken=apitoken)
    userinfo=gu.get()
    if userinfo['status']==0:
        tokenStatus['status']=0
        tokenStatus['token']=apitoken
        tokenStatus['username']=userinfo['data']['username']
    else:
        tokenStatus['status']=1
        tokenStatus['message']='Token past due'
    return tokenStatus

class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        # tk.Tk.title('SBPG')
        self.shared_data={
            "username":tk.StringVar(),
            "password":tk.StringVar(),
            "searchwordid":tk.StringVar(),

        }
        # self.shared_data['password'].set('test')
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)
        # container.wm_title('sbpg')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in (StartPage,LoginPage,userPage):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller=controller
        if not databaseStatus['status']==0:
            messagebox.showinfo("Error", databaseStatus['message'])
            exit(1)
        tokenStatusre=checkTokenStatus()
        if tokenStatusre['status']==0:
            startPageTitle="Hi %s "%tokenStatusre['username']
            label = tk.Label(self, text=startPageTitle, font=LARGE_FONT)
            label.pack(pady=10,padx=10)
            self.controller.shared_data['username'].set(tokenStatusre['username'])
            button = tk.Button(self, text="Search and add",
                                command=lambda: controller.show_frame(userPage))
            button.pack()
        else:
            startPageTitle="Please go to login page to log in shanbay"
            label = tk.Label(self, text=startPageTitle, font=LARGE_FONT)
            label.pack(pady=10,padx=10)

            button = tk.Button(self, text="Login",
                                command=lambda: controller.show_frame(LoginPage))
            button.pack()

class LoginPage(tk.Frame):

    def __init__(self , parent , controller):
        self.controller=controller
        tk.Frame.__init__(self,parent)
        username = StringVar()
        password = StringVar()
        loginContext= StringVar()
        pageTitle=StringVar()
        labelSearchText=StringVar()
        searchword=StringVar()
        labelSearchText.set('Type smoe word you wan search')
        loginContext.set('Please input username and password')
        pageTitle.set('Log into ShanBay')
        
        labelLoginTitle = tk.Label(self,textvariable=pageTitle, font=LARGE_FONT)
        labelLoginTitle.pack(pady=10,padx=10)
        labelStatus = tk.Label(self,textvariable=loginContext)
        labelStatus.pack(pady=10,padx=10)
        labelUsername=tk.Label(self,text="Username/Phone number")
        labelUsername.pack()
        entryUsername=Entry(self,textvariable=username)
        entryUsername.pack()
        labelPassword=tk.Label(self,text="Password")
        labelPassword.pack()
        entryPassword=Entry(self,textvariable=password,show="*")
        entryPassword.pack()
        def printvalue():
            userinfo={}
            gt=getToken(appkey=appkey,username=username.get(),password=password.get())
            apitoken=gt.getshanbayToken()
            if apitoken['status']==0:
                gu=getuserinfo(apitoken=apitoken['token'])
                userinfo=gu.get()
                c = conn.cursor()
                sqlInsertApiToken='INSERT INTO apitoken (apitoken,username) VALUES ( "%s" , "%s" )'%(apitoken['token'],userinfo['data']['username'])
                c.execute(sqlInsertApiToken)
                sqlInsertApiToken='''DELETE from apitokenusing '''
                c.execute(sqlInsertApiToken)
                sqlInsertApiToken='''INSERT INTO apitokenusing (apitoken)
                    VALUES ( "%s")'''%(apitoken['token'])
                c.execute(sqlInsertApiToken)
                conn.commit()
            else:
                loginContext.set("Login failed , Please check your username/password and try again.")
                entryPassword.delete(0,END)
                return
            if userinfo['status']==0:
                self.controller.shared_data['username'].set(userinfo['data']['username'])
                # self.controller.shared_data['apitoken'].set(userinfo[''])
                controller.show_frame(userPage)
                return
            else:
                loginContext.set("Login failed , Please check your username/password and try again.")
                entryPassword.delete(0,"END")
                return
        buttonLogin = tk.Button(self, text="Login",command=printvalue)
        buttonLogin.pack()

class userPage(tk.Frame):

    def __init__(self , parent , controller):
        self.controller=controller
        tk.Frame.__init__(self,parent)
        userPageTitle=StringVar()
        searchwords=StringVar()
        sSearchWord=StringVar()
        sPronunciations=StringVar()
        sWordError=StringVar()
        sDefinition=StringVar()
        
        labelUserPage=tk.Label(self,textvariable=self.controller.shared_data["username"])
        labelUserPage.pack()
        labelsearchStatus=tk.Label(self,textvariable=sWordError)
        labelsearchStatus.pack()


        def addTociku():
            addingWord=self.controller.shared_data['searchwordid'].get()
            c = conn.cursor()
            sqlSelectApiToken='''SELECT apitoken from apitokenusing '''
            sqlApiToken=c.execute(sqlSelectApiToken)
            apitoken=sqlApiToken.fetchone()[0]
            searchWordData=searchandadd(apitoken,searchwords.get())
            s=searchWordData.add()
            if s['status']==0:
                messagebox.showinfo("Success", "Success")
                # sSearchWord.set(addingWord+" add success")
                # self.labelPronunciations.pack_forget()
                # self.labelDefinition.pack_forget()
                # self.buttonAddWord.pack_forget()

            else:
                messagebox.showinfo("Error", s['message'])


        def showTranslate(Translate):
            if not Translate['status']==0:
                sWordError.set("Wrong word ,Please retype and search again")
                return
            sWordError.set("")
            self.controller.shared_data['searchwordid'].set(Translate['data']['id'])
            if sSearchWord.get()=="":
                sSearchWord.set(Translate['word'])
                sPronunciations.set('UK: /'+Translate['data']['pronunciations']['uk']+'/ , US: /'+Translate['data']['pronunciations']['us']+'/')
                sDefinition.set(Translate['data']['definition'])
                self.labelSearchWord=tk.Label(self,textvariable=sSearchWord,font=LARGE_FONT)
                self.labelSearchWord.pack()
                self.labelPronunciations=tk.Label(self,textvariable=sPronunciations)
                self.labelPronunciations.pack()
                self.labelDefinition=tk.Label(self,textvariable=sDefinition)
                self.labelDefinition.pack()
                self.buttonAddWord=tk.Button(self,text='Add to "我的词库" ',command=addTociku)
                self.buttonAddWord.pack()

                return
            else:
                sSearchWord.set(Translate['word'])
                sPronunciations.set('UK: /'+Translate['data']['pronunciations']['uk']+'/ , US: /'+Translate['data']['pronunciations']['us']+'/')
                sDefinition.set(Translate['data']['definition'])
                return 
            
            
            
        def searchWord():
            c = conn.cursor()
            sqlSelectApiToken='''SELECT apitoken from apitokenusing '''
            sqlApiToken=c.execute(sqlSelectApiToken)
            apitoken=sqlApiToken.fetchone()[0]
            searchWordData=searchandadd(apitoken,searchwords.get())
            s=searchWordData.search()
            if s['status']==0:
                cc = conn.cursor()
                sqlInsertResult='INSERT INTO searchhistory (word,shanbayid,definition,ukpcs,uspcs) VALUES ( "%s","%s","%s","%s","%s" )'%(searchwords.get(),s["data"]["definition"],str(s["data"]["id"]),s["data"]["pronunciations"]["uk"],s["data"]["pronunciations"]["us"])
                cc.execute(sqlInsertResult)
                conn.commit()
            showTranslate(Translate=s)
        entrySearch=Entry(self,textvariable=searchwords)
        entrySearch.bind('<Return>',lambda x: searchWord())
        entrySearch.pack()

        buttonSearch=tk.Button(self,text="Search Word",command=searchWord)
        buttonSearch.pack()


app = SeaofBTCapp()
app.geometry("800x600")
app.title("SBPG")
if os.path.isfile('sbpg.ico'):
    app.iconbitmap('sbpg.ico')
app.mainloop()

conn.close()