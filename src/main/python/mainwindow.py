# coding=utf-8
from PySide2 import QtCore, QtGui, QtWidgets
from repo import Repo
import dealswidget
import takeswidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.repo = Repo()

        self.dealsWidget = dealswidget.DealsWidget(self)
        self.takesWidget = takeswidget.TakesWidget(self)

        central = QtWidgets.QSplitter(self)
        self.setCentralWidget(central)
        central.addWidget(self.dealsWidget)
        central.addWidget(self.takesWidget)

        # Toolbar
        tb = self.addToolBar("Common")
        tb.setMovable(False)
        tb.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        tb.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        # Toolbar Actions
        style = QtWidgets.QApplication.instance().style()
        tb.addAction(style.standardIcon(QtWidgets.QStyle.SP_DialogOpenButton),"Открыть отчёты IB",).triggered.connect(self._onOpenIb)
        tb.addAction(style.standardIcon(QtWidgets.QStyle.SP_MessageBoxQuestion),"Справка",).triggered.connect(self._onShowHelp)

        # Connects
        self.takesWidget.dealSelected.connect(self.dealsWidget.selectDeal)

    def _onOpenIb(self):
        dlg = QtWidgets.QFileDialog(self, "Выберите файлы отчётов IB в формате CSV", "", "*.csv")
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self._openIb(filenames)

    def _onShowHelp(self):
        QtGui.QDesktopServices.openUrl("https://github.com/flmnvd/3ndfl")

    def _openIb(self, files):
        self.repo.addIbReports(files)
        self.dealsWidget.setRepo(self.repo)
        self.takesWidget.setRepo(self.repo)
