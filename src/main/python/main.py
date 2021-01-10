from mainwindow import MainWindow
from PySide2 import QtWidgets
from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext

    app = QtWidgets.QApplication.instance()
    app.setApplicationName("3ndfl")
    app.setOrganizationName("finhack")
    app.setOrganizationDomain("tech")

    window = MainWindow()
    window.resize(1024, 768)
    window.show()

    window._openIb(["c:/Users/dokvo/3ndfl_reports/my/2018.csv", "c:/Users/dokvo/3ndfl_reports/my/2019.csv", "c:/Users/dokvo/3ndfl_reports/my/2020.csv"])

    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
