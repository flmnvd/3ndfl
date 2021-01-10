# coding=utf-8
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore
from decimal import Decimal
import datatypes
import enum
import typing
from repo import Repo

class Columns(enum.IntEnum):
    TICKER = 0
    DATETIME = enum.auto()
    COUNT = enum.auto()
    PRICE = enum.auto()
    FEE = enum.auto()
    TOTAL = enum.auto()
    RATE = enum.auto()
    TOTAL_RUB = enum.auto()
    PROCEEDS = enum.auto() # For take
    PROCEEDS_RUB = enum.auto() # For take
    TAX = enum.auto() # For take
    __COUNT = enum.auto()
    def count(): return int(Columns.__COUNT)

def decToS(d:Decimal):
    if d!=None:
        return f'{d:.4f}'

class TakesTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent:QtCore.QObject):
        super().__init__(parent)
        self.repo = None

    def setRepo(self, repo:Repo):
        self.beginResetModel()
        self.repo = repo
        self.endResetModel()

    def getDeal(self, idx:QtCore.QModelIndex):
        # Child
        if self._isIdValid(idx.internalId()):
            take = self.repo._takes[idx.parent().row()]
            openDeal = take.openDeals[idx.row()]
            return openDeal.deal
        # Parent
        else:
            take = self.repo._takes[idx.row()]
            return take.closeDeal

    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:
        if role==QtCore.Qt.DisplayRole:
            column = Columns(index.column())
            deal = None
            # Child
            if index.parent().isValid():
                take = self.repo._takes[index.parent().row()]
                openDeal = take.openDeals[index.row()]
                deal = openDeal.deal
                if column==Columns.COUNT:   return decToS(openDeal.count) + ('(осталось: ' + decToS(openDeal.left) + ')' if openDeal.left != 0 else '')
                if column == Columns.PRICE: return decToS(openDeal.price) + ('(до сплита: ' + decToS(deal.price) + ')' if deal.price != openDeal.price else '')
            # Parent
            else:
                take = self.repo._takes[index.row()]
                deal = take.closeDeal
                if column==Columns.COUNT:       return decToS(take.count())
                if column==Columns.TOTAL:       return decToS(deal.total)
                if column==Columns.TOTAL_RUB:   return decToS(deal.totalRub)
                if column==Columns.PROCEEDS:    return decToS(take.proceeds)
                if column==Columns.PROCEEDS_RUB:return decToS(take.proceedsRub)
                if column==Columns.TAX:         return decToS(take.tax)
                if column == Columns.PRICE:     return decToS(deal.price)
            if column==Columns.TICKER:      return deal.ticker
            if column==Columns.DATETIME:    return deal.dateTime.toString("yyyy-MM-dd hh:mm:ss")
            if column==Columns.FEE:         return decToS(deal.fee)
            if column==Columns.RATE:        return decToS(deal.rate) #self.repo.getRate(deal.currency,deal.dateTime.date())

        if role==QtCore.Qt.BackgroundRole:
            take = self.repo._takes[index.row()]
            # Parent
            if not index.parent().isValid():
                if take.left!=0:
                    return QtGui.QColor(180,0,0)

    def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role==QtCore.Qt.DisplayRole and orientation==QtCore.Qt.Horizontal:
            column = Columns(section)
            if column==Columns.TICKER:      return "Тикер"
            if column==Columns.DATETIME:    return "Дата/Время"
            if column==Columns.COUNT:       return "Количество"
            if column==Columns.PRICE:       return "Цена"
            if column==Columns.FEE:         return "Комиссия"
            if column==Columns.TOTAL:       return "Итого, $"
            if column==Columns.PROCEEDS:    return "Выручка, $"
            if column==Columns.RATE:        return "Курс рубля на дату"
            if column==Columns.TOTAL_RUB:   return "Итого, Руб"
            if column==Columns.PROCEEDS_RUB:return "Выручка, Руб"
            if column==Columns.TAX:         return "Налог 13%, Руб"

    def index(self, row:int, column:int, parent:QtCore.QModelIndex=...) -> QtCore.QModelIndex:
        # Child
        if parent.isValid(): # and not self._isIdValid(parent.internalId()):
            #take = self.repo._takes[parent.row()]
            return self.createIndex(row, column, self._rowToId(parent.row()))
        # Parent
        else:
            return self.createIndex(row, column)
    
    def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
        # Child
        if self._isIdValid(child.internalId()): # and child.column()==0:
            return self.createIndex(self._idToRow(child.internalId()), 0)
        # Parent has no parents
        else:
            return QtCore.QModelIndex()

    def columnCount(self, parent:QtCore.QModelIndex=...) -> int:
        return Columns.count()

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        if self.repo==None: return 0
        if parent.isValid():
            # Child
            if self._isIdValid(parent.internalId()):
                return 0
            # Parent
            else:
                take = self.repo._takes[parent.row()]
                return len(take.openDeals)
        # Root
        else:
            return len(self.repo._takes)

    def _isIdValid(self, id):
        return id!=0

    def _rowToId(self, row):
        return row+1

    def _idToRow(self, id):
        return id-1