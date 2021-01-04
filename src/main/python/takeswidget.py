# coding=utf-8
from PySide2 import QtCore
from PySide2 import QtWidgets
from repo import Repo
import takesmodel
import datatypes

class TakesWidget(QtWidgets.QGroupBox):
    dealSelected = QtCore.Signal(datatypes.Deal)

    def __init__(self, parent:QtWidgets.QWidget):
        super().__init__("Расчёт результата", parent)

        self.table = QtWidgets.QTreeView(self)
        
        self.model = takesmodel.TakesTreeModel(self)
        self.table.setModel(self.model)

        # Bottom
        lblTaxCaption = QtWidgets.QLabel("Всего налог: ")
        self.lblTax = QtWidgets.QLabel()

        # Layout
        lt = QtWidgets.QVBoxLayout(self)
        #lt.setMargin(0)
        lt.addWidget(self.table)

        ltBottom = QtWidgets.QHBoxLayout()
        ltBottom.addWidget(lblTaxCaption)
        ltBottom.addWidget(self.lblTax)
        ltBottom.addStretch()
        lt.addLayout(ltBottom)

        # Connects
        self.table.clicked.connect(self._onItemClicked)

    def setRepo(self, repo:Repo):
        self.model.setRepo(repo)
        self._updateResult()

    def _updateResult(self):
        s = "{} руб.".format(self.model.repo._totalTaxRub)
        self.lblTax.setText(s)

    def _onItemClicked(self, idx:QtCore.QModelIndex):
        deal = self.model.getDeal(idx)
        self.dealSelected.emit(deal)