from mainwindow import MainWindow
from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(1024, 768)
    window.show()
    window._openIb(["c:/Users/dokvo/3ndfl_reports/my-test/2020.csv","c:/Users/dokvo/3ndfl_reports/my-test/2019.csv"])
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
