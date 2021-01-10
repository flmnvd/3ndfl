# coding=utf-8
from PySide2 import QtCore, QtGui, QtWidgets
from repo import Repo
import takesmodel
import datatypes

class TakesWidget(QtWidgets.QGroupBox):
    dealSelected = QtCore.Signal(datatypes.Deal)

    def __init__(self, parent:QtWidgets.QWidget):
        super().__init__("Расчёт результата", parent)

        self.treeView = QtWidgets.QTreeView(self)
        #self.treeView.setAlternatingRowColors(True)
        #self.treeView.verticalHeader().setDefaultSectionSize(QtGui.QFontMetrics(self.treeView.font()).height())

        self.model = takesmodel.TakesTreeModel(self)
        self.treeView.setModel(self.model)

        # Bottom
        lblTaxCaption = QtWidgets.QLabel("Всего налог: ")
        self.lblTax = QtWidgets.QLabel()

        # Layout
        lt = QtWidgets.QVBoxLayout(self)
        #lt.setMargin(0)
        lt.addWidget(self.treeView)

        ltBottom = QtWidgets.QHBoxLayout()
        ltBottom.addWidget(lblTaxCaption)
        ltBottom.addWidget(self.lblTax)
        ltBottom.addStretch()
        lt.addLayout(ltBottom)

        # Connects
        self.treeView.selectionModel().currentChanged.connect(self._onItemClicked)

    def setRepo(self, repo:Repo):
        self.model.setRepo(repo)
        self._updateResult()

    def _updateResult(self):
        s = "{} руб.".format(self.model.repo._totalTaxRub)
        self.lblTax.setText(s)

    def _onItemClicked(self, idx:QtCore.QModelIndex):
        deal = self.model.getDeal(idx)
        self.dealSelected.emit(deal)