from Class_Read_Code import*
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from Class_read_stdout import*

Dic_variable = {}
Dic_file_variable = {}
Dic_constvariable = {}
Dic_file_constvariable = {}

def detect_meaning(string):
    # xoá unit trong chuỗi
    string = re.sub("Unit:\S+|Unit:\S+|unit:\S+|Unit\=\S+:","",string)
    # xoá lsb
    string = re.sub("lsb:\S+|LSB:\S+","",string)
    # xoá các phần k cần thiết
    string = re.sub("\s+\[.+\/.+\]|\d+\S*/\S+|\d+[：:]\S+|[\.\d]+\[.+\]|\t{2,}\d+\S+","",string)
    string = re.sub("\s+"," ",string).strip()
    return string

def AddKeyIfNotExist(Dic, strKey):
	if strKey not in Dic:
		Dic[strKey] = {}

def Export_Enum_Struct(links_source):
    All_file_code = Export_file(links_source)

    list_all_file = All_file_code.List_All_file
    max_file = len(list_all_file)
    progessbar = 1
    progessbar__ = 1
    progessbar_old = 1
    for File in list_all_file:
        # print(File)
        try:
            Data = Typerdef(File)
            Data.read_typedef()
        except:
            print(File, "Export Error!")
        progessbar__ = int((progessbar/max_file)*100)
        if progessbar__ != progessbar_old:
            print(progessbar__)
            progessbar_old = progessbar__
        progessbar += 1
    # print(list(set(Typerdef.Type_const)))
    # result = dict(Typerdef.Typedef_struct, **Typerdef.Typedef_enum)
    save_file_json(".\\Database\\Database_Struct.json",Typerdef.Typedef_struct)
    save_file_json(".\\Database\\Database_Enum.json",Typerdef.Typedef_enum)
    save_file_json(".\\Database\\Database_file_Struct.json",Typerdef.Typedef_file_struct)
    save_file_json(".\\Database\\Database_file_Enum.json",Typerdef.Typedef_file_enum)

    dic_typedef_defaulted = {}
    dic_typedef_defaulted["Const"] = list(set(Typerdef.Type_const))
    dic_typedef_defaulted["Defaulted"] = list(set(Typerdef.Type_defaulted))
    save_file_json(".\\Database\\Database_typedef_defaulted.json",dic_typedef_defaulted)
    print("____________Save Database Struct/Enum Complete!____________")

def read_initial_value(string):
    string = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",string)
    match = re.search("=(.+?);",string)
    if match:
        return match.group(1).strip()
    else:
        return "-"

def Export_variable(links_source):
    global Dic_variable
    global Dic_file_variable
    global Dic_constvariable
    global Dic_file_constvariable
    # Variable_File = "ファイルローカル"
    # Variable_Global = "グローバル"
    Variable_File = "File"
    Variable_Global = "Global"

    All_file_code = Export_file(links_source)
    list_all_file = All_file_code.List_All_file
    max_file = len(list_all_file)
    progessbar = 1
    progessbar__ = 1
    progessbar_old = 1
    for File in list_all_file:
        # print(File)
        try:
            Data = Typerdef(File)
            Data.read_variable()
            AddKeyIfNotExist(Dic_file_variable, Data.name_file_2)
            AddKeyIfNotExist(Dic_file_constvariable, Data.name_file_2)
            for data_value in Data.Variable_4_3:
                _meaning = detect_meaning(data_value[2])
                _name = data_value[0] + re.sub("[\w\*]+","",data_value[1]).replace(" ","")
                _type = data_value[1].replace("[","").replace("]","")
                _range = data_value[0] + "_Range_QA"
                _initial_value = read_initial_value(data_value[4])
                _scope = Variable_File if data_value[4].find("static") != -1 else Variable_Global
                Dic_variable[_name] = [_meaning, _name, _type, _range, "", _initial_value, _scope, ""]
                Dic_file_variable[Data.name_file_2][_name] = [_meaning, _name, _type, _range, "", _initial_value, _scope, ""]
            for data_value in Data.Constant_4_4:
                _meaning = detect_meaning(data_value[2])
                _name = data_value[0] + re.sub("[\w\*]+","",data_value[1]).replace(" ","")
                _type = data_value[1].replace("[","").replace("]","")
                _range = data_value[0] + "_Range_QA"
                _initial_value = read_initial_value(data_value[4])
                _scope = Variable_File if data_value[4].find("static") != -1 else Variable_Global
                Dic_constvariable[_name] = [_meaning, _name, _type, _range, "", _initial_value, _scope, ""]
                Dic_file_constvariable[Data.name_file_2][_name] = [_meaning, _name, _type, _range, "", _initial_value, _scope, ""]
        except:
            print(File, "Export Error!")
        progessbar__ = int((progessbar/max_file)*100)
        if progessbar__ != progessbar_old:
            print(progessbar__)
            progessbar_old = progessbar__
        progessbar += 1
    save_file_json(".\\Database\\Database_variable.json",Dic_variable)
    save_file_json(".\\Database\\Database_file_variable.json",Dic_file_variable)
    save_file_json(".\\Database\\Database_constvariable.json",Dic_constvariable)
    save_file_json(".\\Database\\Database_file_constvariable.json",Dic_file_constvariable)
    print("____________Save Database Variable Complete!____________")

class Thread_Export_database(QtCore.QThread):
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
            self.Export_Enum_Struct_database()
        elif self.index == 2:
            self.Export_Variable_database()
        # elif self.index == 3:
        #     self.Insert_in_DD()
        # elif self.index == 4:
        #     self.Fix_font_size_DD()
        # elif self.index == 5:
        #     self.create_all_DD_common()
        self.capturing.stop()

    def Export_Enum_Struct_database(self):
        try:
            Export_Enum_Struct(self.Data_Gui[0])
        except:
            self.signal.emit("Export Enum_Struct Errors!")

    def Export_Variable_database(self):
        try:
            Export_variable(self.Data_Gui[0])
        except:
            self.signal.emit("Export Variable Errors!")

    def stop(self):
        self.terminate()

    def on_read(self,line):
        self.capturing.print(line)



if __name__ == "__main__":

    links_source = r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)"
    # Export_Enum_Struct(links_source)
    Export_variable(links_source)

    # links = r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)\Common\MDL\IF\if_mdl_VoltageSensorAbstr.h"
    # Data = Typerdef(links)
    # Data.read_variable()
    # print(Data.Variable_4_3)
    