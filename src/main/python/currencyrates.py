from PySide2.QtCore import Qt
from PySide2.QtCore import QDateTime
from PySide2.QtCore import QDate
from xml.etree import ElementTree
from decimal import Decimal
from currency import currencies
import requests

CBDATEFORMAT = "dd/MM/yyyy" # 01/01/2002

# CB HOW TO http://www.cbr.ru/development/sxml/
def getCbRates(sCurrency:str, fromDate, toDate):
    # http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=02/03/2001&date_req2=14/03/2020&VAL_NM_RQ=R01235
    url = "http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={}&date_req2={}&VAL_NM_RQ={}".format(fromDate.toString(CBDATEFORMAT),toDate.toString(CBDATEFORMAT),currencies[sCurrency])
    r = requests.get(url)
    #print(r.status_code,r.text)
    if r.status_code!=200:
        raise Exception("Can't download currency rates. Check Internet connection. "+url)
    
    rates = {}

    root = ElementTree.fromstring(r.text)
    for rec in root:
        date = QDate.fromString(rec.attrib["Date"], "dd.MM.yyyy") # "06.03.2001"
        #date.setTimeSpec(Qt.UTC)
        nominal = Decimal(rec.find("Nominal").text.replace(',','.'))
        value = Decimal(rec.find("Value").text.replace(',','.')) # 28,6600
        rate = nominal*value
        rates[date] = rate
    return rates

def getCbRate(sCurrency:str, date):
    url = "http://www.cbr.ru/scripts/XML_daily.asp?date_req={}".format(date.toString(CBDATEFORMAT))
    r = requests.get(url)
    if r.status_code!=200:
        raise Exception("Can't download currency rate. Check Internet connection. "+url)

    id = currencies[sCurrency]

    root = ElementTree.fromstring(r.text)
    for valute in root:
        if valute.attrib["ID"]==id:
            nominal = Decimal(valute.find("Nominal").text.replace(',','.'))
            value = Decimal(valute.find("Value").text.replace(',','.')) # 28,6600
            rate = nominal*value
            return rate
    raise Exception("Unable to find "+sCurrency+" in CBRF answer "+url)

if __name__ == '__main__':
    #from pycbrf import ExchangeRates
    #rates = ExchangeRates('2020-12-13', locale_en=True)
    #print(rates['AMD'])
    getCbRates("CAD", QDate(2020,1,1), QDateTime.currentDateTime())