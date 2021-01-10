from PySide2 import QtGui, QtWidgets
from repo import Repo
import dealsmodel

class DealsWidget(QtWidgets.QGroupBox):
    def __init__(self, parent:QtWidgets.QWidget):
        super().__init__("Список сделок", parent)

        self.table = QtWidgets.QTableView(self)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(QtGui.QFontMetrics(self.table.font()).height())
        self.table.verticalHeader().hide()

        self.model = dealsmodel.DealsTableModel(self)
        self.table.setModel(self.model)

        lt = QtWidgets.QVBoxLayout(self)
        #lt.setMargin(0)
        lt.addWidget(self.table)

    def setRepo(self, repo:Repo):
        self.model.setRepo(repo)

    def selectDeal(self, deal):
        row = self.model.getDealRow(deal)
        idx = self.model.index(row,0)
        self.table.setCurrentIndex(idx)