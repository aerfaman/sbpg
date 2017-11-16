import requests
import re
import json
from getToken import getToken

class searchandadd:
    def __init__(self, apitoken, word):
        self.apitoken=apitoken
        self.word=word
        self.geturl=r'https://api.shanbay.com/bdc/search/?word=%s'%self.word
        self.posturl=r'https://api.shanbay.com/bdc/learning/'
        self.postjsondata={
            "token":self.apitoken,
            "id":"",
        }
        self.postheaders={
            "Authorization":"Bearer %s"%self.apitoken,
            'content-type': "application/json",
        }
    def search(self):
        r=requests.session()
        s=r.get(self.geturl)
        returndata={}
        text=json.loads(s.text)
        if text['status_code']==0:
            # print(text['data']['cn_definition'])
            returndata['status']=0
            returndata['message']=text['msg']
            returndata['word']=self.word
            returndata['data']=text['data']
        else:
            returndata['status']=1
            returndata['word']=self.word
            returndata['message']=text['msg']
        return returndata

    def add(self):
        searchdata=self.search()
        addstatus={}
        if searchdata['status']==0:
            r=requests.session()
            self.postjsondata['id']=searchdata['data']['content_id']
            s=r.post(self.posturl,json=self.postjsondata,headers=self.postheaders)
            if json.loads(s.text)['status_code']==0:
                addstatus['status']=0
                return addstatus
            else:
                addstatus['status']=1
                addstatus['message']="APIKEY or Network error."
        else:
            addstatus['message']=searchdata['message']
            addstatus['status']=2
        return addstatus
            
