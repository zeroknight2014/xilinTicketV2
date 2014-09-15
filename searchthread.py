__author__ = 'Administrator'
from PyQt5.QtCore import (QThread,pyqtSignal)
import requests
import xlstr


class SearchThread(QThread):
    domain = 'kyfw.12306.cn' #请求域名（真实连接地址）
    host='kyfw.12306.cn' #请求的域名（host）
    http = requests.session()
    stopSignal=False

    searchThreadCallback= pyqtSignal(dict)

    def __init__(self,from_station,to_station,train_date,interval=2,domain=''):
        super(SearchThread,self).__init__()
        if domain!='':
            self.domain=domain

        self.from_station=from_station
        self.to_station=to_station
        self.train_date=train_date
        self.interval=interval

        if not self.load_station_code():
            print('加载车站码异常')

    def run(self):
        while not self.stopSignal:
            ret=self.search_ticket(self.from_station,self.to_station,self.train_date)

            if ret!=False:
                self.searchThreadCallback.emit(ret)


    def search_ticket(self, fromStation, toStation, date):

        headers={'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',"host":self.host}

        url='https://' + self.domain + '/otn/leftTicket/queryT?leftTicketDTO.train_date='+date\
            +"&leftTicketDTO.from_station="+self.stationCode[fromStation]+"&leftTicketDTO.to_station="+\
            self.stationCode[toStation]+"&purpose_codes=ADULT"

        res = self.http.get(url,verify=False,headers=headers)
        ticketInfo=res.json()
        if ticketInfo['status']!=True or ticketInfo['messages']!=[] :
            return False

        if len(ticketInfo['data'])<=0:
            return False

        return ticketInfo['data']

    def load_station_code(self):
        """Load station telcode from 12306.cn

        加载车站电报码，各个请求中会用到
        :raise C12306Error:
        """
        header={"host":self.host}
        res = requests.get('https://'+self.domain+'/otn/resources/js/framework/station_name.js', verify=False,headers=header)
        if res.status_code != 200:
            return False

        stationStrs = xlstr.substr(res.text, "'", "'")
        stationList = stationStrs.split('@')
        stationDict = {}

        for stationStr in stationList:
            station = stationStr.split("|")
            if len(station) > 3:
                stationDict[station[1]] = station[2]

        self.stationCode = stationDict

    def stop(self):
        self.stopSignal=True