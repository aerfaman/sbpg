import requests
import re



gettokenstatus={}

class getToken:
    def __init__(self, appkey,username,password):
        self.appkey=appkey
        self.apiuri=r'api.shanbay.com/api/v1/oauth2/authorize/?client_id=%s&response_type=token'%self.appkey
        self.getTokenUrl=r'https://%s'%self.apiuri
        self.username=username
        self.password=password
        # self.postTokenUrl=r'https://api.shanbay.com/oauth2/login/?next=/%s'%self.apiuri
        self.postTokenUrl=r'https://api.shanbay.com/oauth2/login/?next=/api/v1/oauth2/authorize/%3Fclient_id%3D'+self.appkey+r'%26response_type%3Dtoken'
    def print(self):
        # getTokenUrl=r'https://%s'%self.apiuri
        # postTokeUrl=r'https://api.shanbay.com/oauth2/login/?next=/%s'%self.apiuri
        print(self.postTokenUrl)

    def getshanbayToken(self):
        headers = {
            "Connection":"keep-alive",
            "Host": "api.shanbay.com",
            "Connection":"keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer":self.postTokenUrl,
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        }

        data = {
            "csrfmiddlewaretoken":"",
            "username": self.username,
            "password": self.password,
            "token":"",
            "allow":"登录",
        }
        r=requests.Session()
        s=r.get(self.postTokenUrl)
        data['csrfmiddlewaretoken']=r.cookies['csrftoken']
        ss=r.post(self.postTokenUrl,data=data,headers=headers)
        s=r.get(self.getTokenUrl)
        data2={
            "csrfmiddlewaretoken":"",
            "redirect_uri":r"https://api.shanbay.com/oauth2/auth/success/",
            "scope":"write",
            "client_id":self.appkey,
            "state":"",
            "response_type":"token",
            "allow":"授权",
        }
        headers3={
            "Host": "api.shanbay.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": self.getTokenUrl,
            # "Cookie": csrftoken=OwSAu8BFs3TxqrkZ2rsfRLE2XXSywisF; sessionid=".eJyrVopPLC3JiC8tTi2KT0pMzk7NS1GyUkrOz83Nz9MDS0FFi_UCUotyM4uLM_PznFJTnaBqdZANyATqNTI1NzQxtqwFAAbNIJM:1eAt3d:CClCDHE7BnnV1f3jsfsAddpKIIw"; userid=2571439
            "Connection": "keep-alive",
        }
        data2['csrfmiddlewaretoken']=r.cookies['csrftoken']
        sss=r.post(self.getTokenUrl,data=data2,headers=headers3)
        tokenre=re.match(r"^.*access_token=(.*)\&token_type",sss.url)
        if tokenre==None:
            gettokenstatus['status']=1
            gettokenstatus['message']="failed"
            
        else:
            gettokenstatus['status']=0
            gettokenstatus['message']="success"
            gettokenstatus['token']=tokenre.group(1)
        return(gettokenstatus)
