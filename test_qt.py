# import sys
# import os
# from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QFileDialog, QVBoxLayout

# class MyApp(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.window_width, self.window_height = 800, 200
#         self.setMinimumSize(self.window_width, self.window_height)

#         layout = QVBoxLayout()
#         self.setLayout(layout)

#         self.options = ('Get File Name', 'Get File Names', 'Get Folder Dir', 'Save File Name')

#         self.combo = QComboBox()
#         self.combo.addItems(self.options)
#         layout.addWidget(self.combo)

#         btn = QPushButton('Launch')
#         btn.clicked.connect(self.launchDialog)
#         layout.addWidget(btn)

#     def launchDialog(self):
#         option = self.options.index(self.combo.currentText())

#         if option == 0:
#             response = self.getFileName()
#         elif option == 1:
#             response = self.getFileNames()
#         elif option == 2:
#             response = self.getDirectory()
#         elif option == 3:
#             response = self.getSaveFileName()
#         else:
#             print('Got Nothing')

#     def getFileName(self):
#         file_filter = 'All (*.*);; Excel File (*.xlsx *.xls)'
#         response = QFileDialog.getOpenFileName(
#             parent=self,
#             caption='Select a data file',
#             directory="C:\\Projects",
#             filter=file_filter,
#             initialFilter='All (*.*)'
#         )
#         print(response)
#         return response[0]

#     def getFileNames(self):
#         file_filter = 'Data File (*.xlsx *.csv *.dat);; Excel File (*.xlsx *.xls)'
#         response = QFileDialog.getOpenFileNames(
#             parent=self,
#             caption='Select a data file',
#             directory=os.getcwd(),
#             filter=file_filter,
#             initialFilter='Excel File (*.xlsx *.xls)'
#         )
#         return response[0]

#     def getDirectory(self):
#         response = QFileDialog.getExistingDirectory(
#             self,
#             caption='Select a folder'
#         )
#         print(response)
#         return response 

#     def getSaveFileName(self):
#         file_filter = 'Data File (*.xlsx *.csv *.dat);; Excel File (*.xlsx *.xls)'
#         response = QFileDialog.getSaveFileName(
#             parent=self,
#             caption='Select a data file',
#             directory= 'Data File.dat',
#             filter=file_filter,
#             initialFilter='Excel File (*.xlsx *.xls)'
#         )
#         print(response)
#         return response[0]

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     app.setStyleSheet('''
#         QWidget {
#             font-size: 35px;
#         }
#     ''')
    
#     myApp = MyApp()
#     myApp.show()

#     try:
#         sys.exit(app.exec_())
#     except SystemExit:
#         print('Closing Window...')

from hashlib import new
from operator import truediv
from tkinter import *
from tkinter import filedialog
import tkinter
from docx import Document
import re
import copy
from docx import document
from docx.shared import Pt
from docx.enum.style import WD_STYLE_TYPE
import docx
from docx.shared import RGBColor
from docx.enum.table import WD_ROW_HEIGHT_RULE
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from docx.shared import RGBColor
import os
from Class_write_excel import *
from Class_Convert_katakana import *
from docx.text.paragraph import Paragraph
from docx.oxml.xmlchemy import OxmlElement
from datetime import datetime
import shutil
from Class_Read_Code import *
import docx2txt



def AcceptAll_change(path):
    file_path = path.replace("/","\\")
    import win32com
    from win32com import client
    try:
        word = client.gencache.EnsureDispatch('Word.Application')
    except AttributeError:
        # Remove cache and try again.
        MODULE_LIST = [m.__name__ for m in sys.modules.values()]
        for module in MODULE_LIST:
            if re.match(r'win32com\.gen_py\..+', module):
                del sys.modules[module]
        shutil.rmtree(os.path.abspath(os.path.join(win32com.__gen_path__, '..')))
        from win32com import client
        word = client.gencache.EnsureDispatch('Word.Application')


    word.Visible = False
    doc = word.Documents.Open(file_path )
    # Accept all revisions
    word.ActiveDocument.Revisions.AcceptAll()
    word.ActiveDocument.Save()
    doc.Close(False)
    word.Application.Quit()

    strCurrentPath_update_toc = os.getcwd() + "\\temp\\DD_accept_trackchange"

    if not os.path.exists(strCurrentPath_update_toc):
        string_mkdir = 'mkdir ' + '"'+ strCurrentPath_update_toc + '"'
        os.popen(string_mkdir).read()

    name_file = path.replace("/","\\").split("\\")[-1]
    path_accept_trackchange = strCurrentPath_update_toc
    path_accept_trackchange += "\\" + name_file  
    if os.path.exists(path_accept_trackchange):
        os.remove(path_accept_trackchange)
    shutil.move(file_path, path_accept_trackchange)

    return path_accept_trackchange


AcceptAll_change(r"C:\Projects\Schaeffler_Phase_3\01_Working\05_Output_DD\01_DesignDocument\FS20002-S64010-267 SW detailed design(DcDcCtrl_ISR).docx")