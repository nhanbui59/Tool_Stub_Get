from Class_Stub import*
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from Class_read_stdout import*
from Class_Stub import *

string_C = \
        """
/*************************************************************************************************/
**************************************************************************************************

==>>--------------------------For file AMSTB_SrcFile.c-----------------------------------------<<==

**************************************************************************************************
/*************************************************************************************************/
        """
string_H = \
        """
/*************************************************************************************************/
**************************************************************************************************

==>>-----------------------For file AMSTB_ArySizeDef.h-----------------------------------------<<==

**************************************************************************************************
/*************************************************************************************************/
        """
string_List_of_stub_functions = \
        """
/*************************************************************************************************/
**************************************************************************************************

==>>-----------------------For List_of_stub_functions-----------------------------------------<<==

**************************************************************************************************
/*************************************************************************************************/
        """

class Thread_Stub(QtCore.QThread):
    signal = pyqtSignal(str)
    
    def __init__(self, index = 0,tuple = ()) -> None:
        super().__init__()
        self.index = index
        self.Data_Gui = tuple
        self.capturing = Capturing(self.signal)

    def run(self):
        self.capturing.on_readline(self.on_read)
        self.capturing.start()
        print("start Multithreaded_data_processing_class: ", self.index)
        if self.index == 1:
            self.Export_stub_for_function()
        elif self.index == 2:
            self.Export_stub_for_function_check_optimize()
        elif self.index == 3:
            self.Export_database_function()
        elif self.index == 4:
            self.Export_for_UT_I_O()
        elif self.index == 5:
            self.Export_stub_for_IO_check_optimize()
        elif self.index == 6:
            self.Export_stub_for_function_check_optimize_not_stub()
            callDatebase()
        self.capturing.stop()

    def Export_database_function(self):
        try:
            print("Waiting and reading data from source code !!!!!!")
            export_database_function(self.Data_Gui[0])
            print("Export database function complete !")
        except:
            self.signal.emit("Export database function Errors!")

    def Export_stub_for_function(self):
        try:
            _string_Stub = export_stub_for_function(self.Data_Gui[0])
            self.signal.emit(string_C)
            self.signal.emit(_string_Stub[0])
            self.signal.emit(string_H)
            self.signal.emit(_string_Stub[1])
            self.signal.emit(string_List_of_stub_functions)
            self.signal.emit(_string_Stub[2])
        except:
            self.signal.emit("Export stub for function Errors !!!")

    def Export_stub_for_function_check_optimize(self):
        try:
            string = self.Data_Gui[0].split("|")

            path_check_optimize = self.Data_Gui[1]
            path_check_optimize = path_check_optimize + "\\" +  string[1].strip() + "\\Nidec_Lib_link_test.map"
            function = string[0].strip()

            check_optimize = Read_code(path_check_optimize)
            string_check_optimize = check_optimize.source_code
                       
            _string_Stub = export_stub_for_function_check_optimize(function,string_check_optimize,self.Data_Gui[2],[],[],[]) 
            self.signal.emit(string_C)
            self.signal.emit(_string_Stub[0])
            self.signal.emit(string_H)
            self.signal.emit(_string_Stub[1])
            self.signal.emit(string_List_of_stub_functions)
            self.signal.emit(_string_Stub[2])
        except:
            self.signal.emit("Export stub for function Errors !!!")

    def Export_for_UT_I_O(self):
        try:
            _string_Stub = export_stub_for_sheet_IO(self.Data_Gui[0])
            if isinstance(_string_Stub,list):
                self.signal.emit("\n".join(_string_Stub))
            else:
                self.signal.emit(_string_Stub)
        except:
            self.signal.emit("Export stub for sheet I/O Errors !!!")

    def Export_stub_for_IO_check_optimize(self):
        try:
            string = self.Data_Gui[0].split("|")

            path_check_optimize = self.Data_Gui[1]
            path_check_optimize = path_check_optimize + "\\" +  string[1].strip() + "\\Nidec_Lib_link_test.map"
            function = string[0].strip()

            check_optimize = Read_code(path_check_optimize)
            string_check_optimize = check_optimize.source_code
                       
            _string_Stub = export_stub_for_IO_check_optimize(function,string_check_optimize,[]) 
            if isinstance(_string_Stub,list):
                self.signal.emit("\n".join(_string_Stub))
            else:
                self.signal.emit(_string_Stub)
        except:
            self.signal.emit("Export stub for sheet I/O Errors !!!")

    def Export_stub_for_function_check_optimize_not_stub(self):
        try:
            string = self.Data_Gui[0].split("|")

            path_check_optimize = self.Data_Gui[1]
            path_check_optimize = path_check_optimize + "\\" +  string[1].strip() + "\\Nidec_Lib_link_test.map"
            function = string[0].strip()

            check_optimize = Read_code(path_check_optimize)
            string_check_optimize = check_optimize.source_code
                       
            _string_Stub = export_stub_for_function_check_optimize_not_stub(function,string_check_optimize,self.Data_Gui[2],[],[],[]) 
            self.signal.emit(string_C)
            self.signal.emit(_string_Stub[0])
            self.signal.emit(string_H)
            self.signal.emit(_string_Stub[1])
            self.signal.emit(string_List_of_stub_functions)
            self.signal.emit(_string_Stub[2])
        except:
            self.signal.emit("Export stub for function Errors !!!")


    def stop(self):
        self.terminate()

    def on_read(self,line):
        self.capturing.print(line)



if __name__ == "__main__":

    pass
    