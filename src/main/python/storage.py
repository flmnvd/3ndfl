from PySide2 import QtWidgets
from PySide2.QtCore import QSettings
from PySide2.QtCore import QDate
from decimal import Decimal

def storeCurrencyRates(currencyRates):
    app = QtWidgets.QApplication.instance()
    settings = QSettings(QSettings.IniFormat, QSettings.UserScope, app.organizationName(), app.applicationName())
    settings.beginGroup("CurrencyRates")
    for currency in currencyRates:
        rates = currencyRates[currency]
        s = ""
        for date in rates:
            s += date.toString("yyyyMMdd") + ':' + str(rates[date]) + ';'
        settings.setValue(currency, s[:-1])
    settings.endGroup()
    #print("=============", settings.fileName())

def loadCurrencyRates():
    app = QtWidgets.QApplication.instance()
    settings = QSettings(QSettings.IniFormat, QSettings.UserScope, app.organizationName(), app.applicationName())
    currencyRates = {}
    settings.beginGroup("CurrencyRates")
    for currency in settings.childKeys():
        rates = {}
        for srate in settings.value(currency).split(';'):
            if len(srate)==0: continue
            date, rate = srate.split(':')
            date = QDate.fromString(date,"yyyyMMdd")
            rates[date] = Decimal(rate)
        currencyRates[currency] = rates
    settings.endGroup()
    return currencyRates

"""
def storeRates(currencyRates):
    from PySide2.QtCore import QSettings
    settings = QSettings()
    settings.setValue("CurrencyRates", currencyRates)

    for currency in currencyRates:
        rates = currencyRates[currency]
        settings.beginGroup(currency)
        settings.endGroup()"""