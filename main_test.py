from operator import index
import time
import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from Gui import Ui_MainWindow
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QSizePolicy, QApplication
from PyQt5.QtWidgets import *
from Class_inert_DD import*
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from Class_read_stdout import*
from Class_Export_database import*

try:
    g_setting = read_file_json(".\\Database\\Setting.json")
except:
    print("Not exits setting")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)
        self.uic.tabWidget.tabBar().setVisible(False)
        self.uic.actionSetting.triggered.connect(self.enable_export)
        self.uic.tabWidget.setCurrentWidget(self.uic.tab)
        self.uic.actionExport_Database.triggered.connect(self.tab_2)
        self.uic.actionTool_DD.triggered.connect(self.tab)
        self.uic.pushButton.clicked.connect(self.start_create_new_common_DD)
        self.uic.pushButton_4.clicked.connect(self.start_Insert_in_DD)
        self.uic.pushButton_5.clicked.connect(self.Open_folder_temp)
        self.uic.pushButton_3.clicked.connect(self.start_Fix_font_size_DD)
        self.uic.pushButton_7.clicked.connect(self.start_export_database_macro)
        self.uic.pushButton_8.clicked.connect(self.start_Create_all_common)
        self.uic.pushButton_2.clicked.connect(self.start_Export_Enum_Struct_database)
        self.uic.pushButton_6.clicked.connect(self.start_Export_Variable_database)
        self.uic.pushButton_7.setEnabled(False)
        self.uic.pushButton_8.setEnabled(False)
        self.uic.pushButton_9.setEnabled(False)
        self.uic.pushButton_10.setEnabled(False)
        self.uic.lineEdit_3.setText(g_setting["Path project"])
        self.uic.lineEdit_4.setText(g_setting["Path all source code"])

        self.thread = {}
        self.thread_export = {}

    def enable_export(self):
        self.uic.tabWidget.setCurrentWidget(self.uic.tab)
        string = os.popen("whoami").read().strip()
        print(string)
        if string == "geservs\\nhanbuivan" or string == "geservs\\dongtta" :
            self.uic.pushButton_7.setEnabled(True)
            self.uic.pushButton_8.setEnabled(True)
            self.uic.pushButton_9.setEnabled(True)
            self.uic.pushButton_10.setEnabled(True)

    def Open_folder_temp(self):
        strCurrentPath_update_toc = os.getcwd() + "\\temp"
        if not os.path.exists(strCurrentPath_update_toc):
            string_mkdir = 'mkdir ' + '"'+ strCurrentPath_update_toc + '"'
            os.popen(string_mkdir).read()
        cmd_in = 'explorer ' + '"' +strCurrentPath_update_toc + '"'
        subprocess.Popen(cmd_in)
    
    def start_export_database_macro(self):
        path_source_code = self.getDirectory()
        if os.path.exists(path_source_code):
            self.thread[1] = Thread_DD(1,(path_source_code,))
            self.thread[1].start()
            self.thread[1].signal.connect(self.my_function)
        else:
            self.msg_box(path_source_code + " Not exists.\nPlease check path DD again !")


    def start_create_new_common_DD(self):
        self.uic.textEdit.setText("")
        string_path_code = self.uic.lineEdit.text().strip()
        if string_path_code == "":
            self.msg_box("Please enter source code link in Path Code")
        else:          
            self.thread[2] = Thread_DD(2,(string_path_code,))
            self.thread[2].start()
            self.thread[2].signal.connect(self.my_function)

    def start_Insert_in_DD(self):
        self.uic.textEdit.setText("")
        string_path_code = self.uic.lineEdit.text().strip()
        string_path_DD = self.uic.lineEdit_2.text().strip()
        if string_path_DD == "":
            string_path_DD = self.getFileName()
            self.uic.lineEdit_2.setText(string_path_DD)
        if string_path_code == "":
            self.msg_box("Please enter source code link in Path Code")
        else:
            self.thread[3] = Thread_DD(3,(string_path_code,string_path_DD))
            self.thread[3].start()
            self.thread[3].signal.connect(self.my_function)

    def start_Fix_font_size_DD(self):
        self.uic.textEdit.setText("")
        string_path_DD = self.uic.lineEdit_2.text().strip()
        if string_path_DD == "":
            string_path_DD = self.getFileName()
            self.uic.lineEdit_2.setText(string_path_DD)
        if os.path.exists(string_path_DD):
            self.thread[4] = Thread_DD(4,(string_path_DD,))
            self.thread[4].start()
            self.thread[4].signal.connect(self.my_function)
        else:
            self.msg_box(string_path_DD + " Not exists.\nPlease check path DD again !")

    def start_Create_all_common(self):
        self.uic.textEdit.setText("")
        string_path_Source = self.getDirectory().replace("/","\\")
        match_assignment = re.search(".+01_Source_Code",string_path_Source)
        string_path_assignment = ""
        if match_assignment:
            match_assignment = re.search(".+01_Working",string_path_Source).group()
            string_path_assignment = match_assignment + "\\03_Documents\\06_Assignment\\00_Detail_Assignment.xlsx"
            self.uic.textEdit.setText(string_path_Source + "\n" + string_path_assignment)
            self.thread[5] = Thread_DD(5,(string_path_Source,string_path_assignment))
            self.thread[5].start()
            self.thread[5].signal.connect(self.my_function)
        else:
            self.msg_box(" Not exists source code.\nPlease check path source code again !")
    
    def my_function(self, string):
        i = self.sender().index
        if i in [1,2,3,4,5]:
            string_edittex = self.uic.textEdit.toPlainText()
            string_edittex = self.settext_edit(string_edittex,string)
            self.uic.textEdit.setText(string_edittex)
            self.uic.textEdit.moveCursor(QtGui.QTextCursor.End)

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
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='All (*.*)'
        )
        return response[0]

    def getDirectory(self):
        response = QFileDialog.getExistingDirectory(
            self,
            caption='Select a folder'
        )
        return response 

    def tab_2(self):
        self.uic.tabWidget.setCurrentWidget(self.uic.tab_2)
    def tab(self):
        self.uic.tabWidget.setCurrentWidget(self.uic.tab)

    def start_Export_Enum_Struct_database(self):
        self.uic.textEdit_2.setText("")
        self.uic.progressBar.setProperty("value", 0)
        string_path_source = self.uic.lineEdit_4.text().strip()
        if string_path_source == "":
            self.msg_box("Please check path source code again !")
        else: 
            self.thread_export[1] = Thread_Export_database(1,(string_path_source,))
            self.thread_export[1].start()
            self.thread_export[1].signal.connect(self.my_function_export)

    def start_Export_Variable_database(self):
        self.uic.textEdit_2.setText("")
        self.uic.progressBar.setProperty("value", 0)
        string_path_source = self.uic.lineEdit_4.text().strip()
        if string_path_source == "":
            self.msg_box("Please check path source code again !")
        else:
            self.thread_export[2] = Thread_Export_database(2,(string_path_source,))
            self.thread_export[2].start()
            self.thread_export[2].signal.connect(self.my_function_export)

    def my_function_export(self, string):
        i = self.sender().index
        if i in [1, 2]:
            try:
                self.uic.progressBar.setValue(int(string))
            except:
                string_edittex = self.uic.textEdit_2.toPlainText()
                string_edittex = self.settext_edit(string_edittex,string)
                self.uic.textEdit_2.setText(string_edittex)
                self.uic.textEdit_2.moveCursor(QtGui.QTextCursor.End)


class Thread_DD(QtCore.QThread):
    signal = pyqtSignal(str)
    
    def __init__(self, index = 0,tuple = ()) -> None:
        super().__init__()
        self.index = index
        self.Data_Gui = tuple
        self.capturing = Capturing(self.signal)

    def run(self):
        self.capturing.on_readline(self.on_read)
        self.capturing.start()
        print("start thread: ", self.index)
        if self.index == 1:
            self.export_database_macro()
        elif self.index == 2:
            self.create_new_common_DD()
        elif self.index == 3:
            self.Insert_in_DD()
        elif self.index == 4:
            self.Fix_font_size_DD()
        elif self.index == 5:
            self.create_all_DD_common()
        self.capturing.stop()

    def stop(self):
        self.terminate()

    def export_database_macro(self):
        try:
            links_source = self.Data_Gui[0]
            All_file_code = Export_file(links_source)
            list_data_define = []
            for File in All_file_code.List_All_file:
                Data = Typerdef(File)
                list_data_define.extend(Data.read_define())
            exxcel = write_excel("Database.xlsx")
            exxcel.write("Define",list_data_define)
            exxcel.save()
            exxcel_database = Read_excel("Database.xlsx")
            exxcel_database.save_database_json()
            self.signal.emit("Export database macro complete")
        except:
            self.signal.emit("Export database macro Errors!")

    def create_new_common_DD(self):
        try:
            string_path_code = self.Data_Gui[0]
            self.signal.emit("Create file common DD\nPath code: "+string_path_code)
            Data = Typerdef(string_path_code)
            Data.read_define()
            Data.read_variable()
            Data.read_typef_enum()
            Data.read_typedef_struct()
            document = Word_("",string_path_code,new=True)
            document.creat_enum(Data.Enum_4_1)
            document.creat_Struct(Data.Struct_4_2)
            document.creat_define(Data.Macro_4_5)
            document.creat_g_variable(Data.Variable_4_3)
            document.save()
            self.signal.emit("Export DD common Complete !")
        except:
            self.signal.emit("Export DD common Error !")

    def Insert_in_DD(self):
        # try:
            string_path_code = self.Data_Gui[0]
            self.signal.emit("Path Code:\n" + string_path_code)
            string_path_DD = self.Data_Gui[1]
            Data = Typerdef(string_path_code)
            Data.read_define()
            Data.read_variable()
            Data.read_typef_enum()
            Data.read_typedef_struct()
            self.signal.emit("Read data source code done!")
            if os.path.exists(string_path_DD):
                self.signal.emit("Path DD:\n" + string_path_DD)
                document = Word_(string_path_DD,string_path_code)
                document.insert_DD_enum(Data.Enum_4_1)
                self.signal.emit("Insert enum done")
                document.insert_DD_struct(Data.Struct_4_2)
                self.signal.emit("Insert struct done")
                document.insert_DD_variable(Data.Variable_4_3)
                self.signal.emit("Insert global done")
                document.insert_DD_define(Data.Macro_4_5)
                self.signal.emit("Insert macro done")
                self.signal.emit("Saving .....!")
                document.save()
                self.signal.emit("Insert DD common complete !")
            else:
                self.signal.emit(string_path_DD + " Not exists!\nPlease check Path DD again")
        # except:
        #     self.signal.emit("Insert DD common Error !")

    def Fix_font_size_DD(self):
        string_path_DD = self.Data_Gui[0]
        self.signal.emit("Start fix")
        document = Word_(string_path_DD,"",accept_trackchange = True)
        self.signal.emit("Saving.....")
        document.save()
        self.signal.emit("Fix font size and katakana done!")
        self.signal.emit("Path DD:\n" + string_path_DD)
        self.signal.emit("Save done!")

    def on_read(self,line):
        self.capturing.print(line)

    def create_all_DD_common(self):
        List_All_file_c_h = self.read_all_file_source()
        list_source_assignment = self.read_data_assignment()
        for data in list_source_assignment:
            for data_c_h in List_All_file_c_h:
                if data_c_h.find(data) != -1:
                    try:
                        string_path_code = data_c_h
                        Data = Typerdef(string_path_code)
                        Data.read_define()
                        Data.read_variable()
                        Data.read_typef_enum()
                        Data.read_typedef_struct()
                        document = Word_("",string_path_code,new=True)
                        document.creat_enum(Data.Enum_4_1)
                        document.creat_Struct(Data.Struct_4_2)
                        document.creat_define(Data.Macro_4_5)
                        document.creat_g_variable(Data.Variable_4_3)
                        document.save()
                    except:
                        self.signal.emit("Export DD common Error !\n" + string_path_code)
                    break

    def read_data_assignment(self):
        list_source = []
        workbook = openpyxl.load_workbook(self.Data_Gui[1] , data_only=True)
        sheet_data = workbook["TasksList"]
        for i in range(sheet_data.max_row):
            string_file = sheet_data.cell(row=i+1,column=90).value
            if string_file not in list_source:
                list_source.append(str(string_file).replace("\\","/"))
        list_source = list(set(list_source))
        return list_source

    def read_all_file_source(self):
        source = Export_file(self.Data_Gui[0])
        return source.List_All_file


if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())



