# coding=utf-8
from PySide2 import QtWidgets
from PySide2 import QtCore
import datatypes
import enum
import typing
from repo import Repo

class Columns(enum.IntEnum):
    ASSET = 0
    CURRENCY = 1
    TICKER = 2
    EXCHANGE = 3
    DATETIME = 4
    COUNT = 5
    PRICE = 6
    FEE = 7
    OPEN = 8
    RATE = 9
    def count(): return 10

class DealsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent:QtCore.QObject):
        super().__init__(parent)
        self.repo = None

    def setRepo(self, repo:Repo):
        self.beginResetModel()
        self.repo = repo
        self.endResetModel()

    def getDealRow(self, deal):
        row = 0
        for d in self.repo._deals:
            if d is deal:
                return row
            row += 1
        assert False
        return -1

    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:
        if role==QtCore.Qt.DisplayRole or role==QtCore.Qt.ToolTipRole:
            column = Columns(index.column())
            deal = self.repo._deals[index.row()]
            if column==Columns.ASSET:   return deal.assetClass.__str__()
            if column==Columns.CURRENCY:return deal.currency
            if column==Columns.TICKER:
                if deal.dealType == datatypes.DealType.SPLIT or deal.dealType == datatypes.DealType.RENAME:
                    return deal.description
                return deal.ticker + (' ('+deal.origTicker+')' if deal.ticker!=deal.origTicker else "")
            if column==Columns.EXCHANGE:return self.repo._infos[deal.ticker].exchange if deal.ticker in self.repo._infos else ""
            if column==Columns.DATETIME:return deal.dateTime.toString("yyyy-MM-dd hh:mm:ss")
            if column==Columns.COUNT:   return str(deal.count)
            if column==Columns.PRICE:   return str(deal.price)
            if column==Columns.FEE:     return str(deal.fee)
            if column==Columns.OPEN:    return deal.dealType.__str__()
            if column==Columns.RATE:    return str(deal.rate) #self.repo.getRate(deal.currency,deal.dateTime.date())

    def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role==QtCore.Qt.DisplayRole and orientation==QtCore.Qt.Horizontal:
            column = Columns(section)
            if column==Columns.ASSET:   return "Тип актива"
            if column==Columns.CURRENCY:return "Валюта"
            if column==Columns.TICKER:  return "Тикер"
            if column==Columns.EXCHANGE:return "Биржа"
            if column==Columns.DATETIME:return "Дата/Время"
            if column==Columns.COUNT:   return "Количество"
            if column==Columns.PRICE:   return "Цена"
            if column==Columns.FEE:     return "Комиссия"
            if column==Columns.OPEN:    return "Отк/Закр"
            if column==Columns.RATE:    return "Курс рубля на дату"

    def columnCount(self, parent:QtCore.QModelIndex=...) -> int:
        return Columns.count()

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        if self.repo==None: return 0
        return len(self.repo._deals)
