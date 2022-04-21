from pkgutil import read_code
import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from Gui_Stub import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from Multithreaded_data_processing_class import *

try:
    g_setting = read_file_json(".\\Database\\Setting.json")
    print("Load data ok")
except:
    print("Not exits setting")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)
        self.uic.tabWidget.tabBar().setVisible(False)
        self.uic.actionExport_all_stub.triggered.connect(self.start_Export_stub_for_function)
        self.uic.actionExport_Database.triggered.connect(self.start_Export_database_function)
        self.uic.actionExport_for_UT_I_O.triggered.connect(self.start_Export_for_UT_I_O)
        self.uic.actionExport_check_optimize.triggered.connect(self.start_Export_stub_for_function_check_optimize)
        self.uic.actionExport_for_UT_IO_check_optimize.triggered.connect(self.start_Export_stub_for_IO_check_optimize)
        self.uic.actionExport_check_optimize_not_check_stub.triggered.connect(self.start_Export_stub_for_function_check_optimize_not_stub)
        self.uic.progressBar.setHidden(True)

        #### luồng xử lý sub function và gen stub @@@@@@@
        self.Thread_Stub = {}

    ################ xử lý chính ################
    def my_function(self, string):
        i = self.sender().index
        if i == 3:
            try:
                self.uic.progressBar.setValue(int(string))
            except:
                string_edittex = self.uic.textEdit.toPlainText()
                string_edittex = self.settext_edit(string_edittex,string)
                self.uic.textEdit.setText(string_edittex)
                self.uic.textEdit.moveCursor(QtGui.QTextCursor.End)
        elif i in [0, 1, 2, 4, 5, 6]:
            string_edittex = self.uic.textEdit.toPlainText()
            string_edittex = self.settext_edit(string_edittex,string)
            self.uic.textEdit.setText(string_edittex)
            self.uic.textEdit.moveCursor(QtGui.QTextCursor.End)
    ################ ______________ ################

    ################ xử lý các chức năng ######################
    def start_Export_stub_for_function(self):
        self.uic.progressBar.setHidden(True)
        self.uic.textEdit.setText("")
        string_function = self.uic.lineEdit.text().strip()
        if string_function == "":
            self.msg_box("Please check function again !")
        else:
            self.Thread_Stub[1] = Thread_Stub(1,(string_function,))
            self.Thread_Stub[1].start()
            self.Thread_Stub[1].signal.connect(self.my_function)

    def start_Export_stub_for_function_check_optimize(self):
        self.uic.progressBar.setHidden(True)
        self.uic.textEdit.setText("")
        string_function = self.uic.lineEdit.text().strip()
        if string_function == "" or string_function.find("|") == -1:
            self.uic.textEdit.setText("Exemple:\n  ==>> Function|Environment")
            self.msg_box("Please check function and environment !!!")
        else:
            try:
                code_stub = Read_code(g_setting["Path project"] + "\\04_Output\\04_SourceCode\\01_Stub\\AMSTB_SrcFile.c")
                string_code_stub = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",code_stub.source_code)
            except:
                string_code_stub = ""
            self.Thread_Stub[2] = Thread_Stub(2,(string_function,g_setting["Path check optimize"],string_code_stub,))
            self.Thread_Stub[2].start()
            self.Thread_Stub[2].signal.connect(self.my_function)

    def start_Export_database_function(self):
        self.uic.progressBar.setHidden(False)
        self.uic.textEdit.setText("")
        self.uic.progressBar.setProperty("value", 0)
        string_path_source = self.getDirectory()
        if string_path_source == "":
            self.msg_box("Please check path source code again !")
        else:
            self.Thread_Stub[3] = Thread_Stub(3,(string_path_source,))
            self.Thread_Stub[3].start()
            self.Thread_Stub[3].signal.connect(self.my_function)

    def start_Export_for_UT_I_O(self):
        self.uic.progressBar.setHidden(True)
        self.uic.textEdit.setText("")
        string_function = self.uic.lineEdit.text().strip()
        if string_function == "":
            self.msg_box("Please check function again !")
        else:
            self.Thread_Stub[4] = Thread_Stub(4,(string_function,))
            self.Thread_Stub[4].start()
            self.Thread_Stub[4].signal.connect(self.my_function)

    def start_Export_stub_for_IO_check_optimize(self):
        self.uic.progressBar.setHidden(True)
        self.uic.textEdit.setText("")
        string_function = self.uic.lineEdit.text().strip()
        if string_function == "" or string_function.find("|") == -1:
            self.uic.textEdit.setText("Exemple:\n  ==>> Function|Environment")
            self.msg_box("Please check function and environment !!!")
        else:
            try:
                code_stub = Read_code(g_setting["Path project"] + "\\04_Output\\04_SourceCode\\01_Stub\\AMSTB_SrcFile.c")
                string_code_stub = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",code_stub.source_code)
            except:
                string_code_stub = ""
            self.Thread_Stub[5] = Thread_Stub(5,(string_function,g_setting["Path check optimize"],string_code_stub,))
            self.Thread_Stub[5].start()
            self.Thread_Stub[5].signal.connect(self.my_function)

    def start_Export_stub_for_function_check_optimize_not_stub(self):
        self.uic.progressBar.setHidden(True)
        self.uic.textEdit.setText("")
        string_function = self.uic.lineEdit.text().strip()
        if string_function == "" or string_function.find("|") == -1:
            self.uic.textEdit.setText("Exemple:\n  ==>> Function|Environment")
            self.msg_box("Please check function and environment !!!")
        else:
            try:
                code_stub = Read_code(g_setting["Path project"] + "\\04_Output\\04_SourceCode\\01_Stub\\AMSTB_SrcFile.c")
                string_code_stub = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",code_stub.source_code)
            except:
                string_code_stub = ""
            self.Thread_Stub[6] = Thread_Stub(6,(string_function,g_setting["Path check optimize"],string_code_stub,))
            self.Thread_Stub[6].start()
            self.Thread_Stub[6].signal.connect(self.my_function)



    ################ ___________________ ######################

############################################# default #############################################
    def show(self):
        self.main_win.show()

    def msg_box(self,text = ""):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def settext_edit(self,string_main,string):
        list_tam = [string_main, string]
        string_main = "\n".join(list_tam)
        return string_main

    def getFileName(self):
        file_filter = 'All (*.*);; Excel File (*.xlsx *.xls)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a data file',
            directory=g_setting["Last path selected"],
            filter=file_filter,
            initialFilter='All (*.*)'
        )
        _directory = "/".join(response[0].replace("\\","/").split("/")[0:-1])
        g_setting["Last path selected"] = _directory
        save_file_json(".\\Database\\Setting.json",g_setting)
        return response[0]

    def getDirectory(self):
        response = QFileDialog.getExistingDirectory(
            self,
            caption='Select a folder',
            directory = g_setting["Last path selected"]
        )
        g_setting["Last path selected"] = response
        save_file_json(".\\Database\\Setting.json",g_setting)
        return response

    def test(self):
        self.msg_box("xxx")
########################################### end default ###########################################


if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())



