# -*- coding: utf-8 -*- 
from os import link, name, supports_bytes_environ
import re
from typing import Pattern
import xlwings as xl
import sys
import os.path
# import Class_Word
from Class_read_links_file import *
from Class_Convert_katakana import *
from Class_write_excel import *
import subprocess

class Typerdef:
    Type_defaulted = []
    Type_const = []
    Typedef_struct = {}
    Typedef_enum = {}
    Typedef_file_struct = {}
    Typedef_file_enum = {}
    def __init__(self,path_file_c):
        self.path_file_C = path_file_c
        self.name_file = path_file_c.replace("/","\\").split("\\")[-1]
        self.name_file_2 = self.name_file.replace(".c","").replace(".h","")
        self.__source_code = self.all_line()
        self.Enum_4_1 = []
        self.Struct_4_2 = []
        self.Variable_4_3 = []
        self.Constant_4_4 = []
        self.Macro_4_5 = []

    def all_line(self):    
        with open(self.path_file_C,"r",encoding= "shift-jis",errors="ignore") as s_code:
            all_lines = s_code.read()
            s_code.close()
        return all_lines

    @property
    def source_code(self):
        return self.__source_code
    
    @source_code.setter
    def source_code(self,setter_source):
        self.__source_code = setter_source

    def Detect_meaning(self,string,Type_meaning = "Meaning_variable_enum-None"):
        meaning_ = Type_meaning
        meaning__tam = re.search("\/\*+([\s\S]*?)\*+\/|\/\/(.*)",string)
        if meaning__tam != None:
            try:
                meaning_ = meaning__tam.group(1).strip()
            except:
                meaning_ = meaning__tam.group(2).strip()
        return meaning_

    def read_define(self): #đọc define trong source code
        read_file_C = self.source_code
        lines = read_file_C.split("\n")
        string_tam = ""
        for line in range(len(lines)):
            string_tam += lines[line]
            if string_tam.find("#define") != -1:
                if lines[line].find("\\") != -1:
                    continue
                else:
                    # print(string_tam.strip())
                    if self.conver_define(string_tam.strip()) != None:
                        self.Macro_4_5.append(self.conver_define(string_tam.strip()))
            string_tam = ""

        return self.Macro_4_5

    def conver_define(self,string):
        name = ""
        value = ""
        __check = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",string)
        meaning = "None"
        if re.search("\/\*[\s\S]*?\*\/|\/\/.*",string) :
            meaning = re.search("\/\*[\s\S]*?\*\/|\/\/.*",string).group()
            meaning = re.sub("[\/\*]","",meaning).strip()

        if len(re.findall("[\w]+",__check)) <= 2:
            return None
        else:
            name = re.findall("[\w]+",__check.replace("#define",""))[0].strip()
            value = __check.replace("#define","").replace(name,"").strip()
            if value.find("(") != -1:
                try:
                    value = re.search("\((.+)\)",value).group(1).strip()
                except:
                    pass
        # print(meaning,"--",name,"--",value)
        return [meaning,name,value,self.name_file]

    def read_typef_enum(self):
        read_file_C = self.source_code
        typerdef_enum = read_file_C.split("\n")
        name_enum = ""
        meaning_enum = ""
        Typerdef.Typedef_file_enum[self.name_file_2] = {}
        for line in range(len(typerdef_enum)):
            try:
                if re.search("enum\s+|enum$|enum{",typerdef_enum[line]) != None and re.search("[\w]enum|;",typerdef_enum[line]) == None:
                    name_enum = typerdef_enum[line].replace("typedef","").replace("volatile","").replace("{","").strip()
                    meaning_tam = re.search("\/\*+([\s\S]*?)\*+\/|\/\/(.*)",typerdef_enum[line-1])
                    if meaning_tam != None:
                        meaning_enum = self.Detect_meaning(typerdef_enum[line-1],"Meaning_enum-None")
                    else:
                        meaning_enum = self.Detect_meaning(typerdef_enum[line],"Meaning_enum-None")

                    self.conver_enum(typerdef_enum[line::], name_enum, meaning_enum)
            except:
                continue
        return self.Enum_4_1

    def conver_enum(self,typerdef_enum,name_enum,meaning_enum):
        tydef_enum = ""
        meaning_enum_variable = ""
        enum_variable = ""
        variable_set = 0
        list_enum_tam = []
        for enum in typerdef_enum:
            __check = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",enum)
            if enum.find("}") != -1:
                tydef_enum_tam = re.search("([\w]+);",enum)
                tydef_enum = "Typerdef_enum-None"
                if tydef_enum_tam :
                    tydef_enum = tydef_enum_tam.group(1)
                self.Enum_4_1.append({(meaning_enum,tydef_enum,name_enum):list_enum_tam.copy()})
                list_enum_temp = [["-",meaning_enum,"-"]]
                list_enum_temp.extend(list_enum_tam.copy())
                if tydef_enum == "Typerdef_enum-None":
                    Typerdef.Typedef_enum[name_enum] = list_enum_temp.copy()
                    Typerdef.Typedef_file_enum[self.name_file_2][name_enum] = list_enum_temp.copy()
                else:
                    Typerdef.Typedef_enum[tydef_enum] = list_enum_temp.copy()
                    Typerdef.Typedef_file_enum[self.name_file_2][tydef_enum] = list_enum_temp.copy()
                list_enum_tam = []
                break
            elif (__check.find(",") != -1 or (__check.find("enum") == -1 and __check.find("{") == -1)) and re.search("[\w]",__check) != None :
                meaning_enum_variable = self.Detect_meaning(enum,"Meaning_variable_enum-None")

                # enum_variable = __check.replace(type_variable,"").replace(";","").strip()
                if re.search("=.+",__check) != None:
                    enum_variable = re.sub("=.+","",__check).strip()
                    variable_set = re.search("=\s*([-\w]+)",__check).group(1).strip()
                    variable_set = re.sub("u|l|f|U|L","",variable_set)
                    try:
                        variable_set = int(variable_set,0)
                    except:
                        variable_set = 0
                else:
                    enum_variable = __check.replace(",","").strip()
                    variable_set += 1
                # print(meaning_enum,"**",name_enum,"**",enum_variable,"**",variable_set,"**",meaning_enum_variable)
                list_tam = [enum_variable,variable_set,meaning_enum_variable]
                list_enum_tam.append(list_tam.copy())

    def read_typedef_struct(self):
        read_file_C = self.source_code
        typerdef_struct = read_file_C.split("\n")
        name_struct = ""
        meaning_struct = ""
        Typerdef.Typedef_file_struct[self.name_file_2] = {}
        for line in range(len(typerdef_struct)):
            try:
                if re.search("struct\s+|struct$|struct{",typerdef_struct[line]) != None  and re.search("[\w]struct|;",typerdef_struct[line]) == None:
                    name_struct = typerdef_struct[line].replace("typedef","").replace("volatile","").replace("{","").strip()
                    meaning_tam = re.search("\/\*+([\s\S]*?)\*+\/|\/\/(.*)",typerdef_struct[line-1])
                    if meaning_tam != None:
                        meaning_struct = self.Detect_meaning(typerdef_struct[line-1],"Meaning_struct-None")
                    else:
                        meaning_struct = self.Detect_meaning(typerdef_struct[line],"Meaning_struct-None")    
                    self.conver_struct(typerdef_struct[line::],name_struct,meaning_struct)
                    # print(name_struct,"--", meaning_struct)
            except:
                continue
        return self.Struct_4_2

    def conver_struct(self,typerdef_struct,name_struct,meaning_struct):
        tydef_struct = ""
        meaning_variable = ""
        type_variable = ""
        variable = ""
        list_struct_tam = []
        for struct in typerdef_struct:
            __check = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",struct)
            if struct.find("}") != -1:
                tydef_struct_tam = re.search("([\w]+);",struct)
                tydef_struct = "Typerdef_struct-None"
                if tydef_struct_tam:
                    tydef_struct = tydef_struct_tam.group(1)
                self.Struct_4_2.append({(meaning_struct,tydef_struct,name_struct):list_struct_tam.copy()})
                list_struct_temp = [["-",meaning_struct,"-"]]
                list_struct_temp.extend(list_struct_tam.copy())
                if tydef_struct == "Typerdef_struct-None":
                    Typerdef.Typedef_struct[name_struct] = list_struct_temp.copy()
                    Typerdef.Typedef_file_struct[self.name_file_2][name_struct] = list_struct_temp.copy()
                else:
                    Typerdef.Typedef_struct[tydef_struct] = list_struct_temp.copy()
                    Typerdef.Typedef_file_struct[self.name_file_2][tydef_struct] = list_struct_temp.copy()
                list_struct_tam = []
                break
            elif __check.find(";") != -1:
                Pattern_Type = "FUNC\s*\(.+?\)|P2FUNC\s*\(.+?\)|FUNC_P2VAR\s*\(.+?\)|FUNC_P2CONST\s*\(.+?\)|CONSTP2VAR\s*\(.+?\)|CONSTP2CONST\s*\(.+?\)|P2VAR\s*\(.+?\)|P2CONST\s*\(.+?\)|VAR\s*\(.+?\)|CONST\s*\(.+?\)|volatile\s+[\w\*]+|const\s+[\w\*]+|unsigned\s+[\w\*]+|signed\s+[\w\*]+|[\w\*]+"
                __check = __check.replace("volatile","")

                type_variable = re.search(Pattern_Type,__check).group()
                variable = __check.replace(type_variable,"").replace(";","").strip()
                # type_variable = type_variable.replace("volatile","").strip()

                meaning_variable = self.Detect_meaning(struct,"Meaning_variable_struct-None")

                    # meaning_variable = re.sub("\t\d.+|\s\[.+|Unit:[^\s]+|LSB:[\d\/\.]+|unit:[^\s]+|\*","",meaning_variable).strip()
                # print(meaning_struct,"**",name_struct,"**",type_variable,"**",variable,"**",meaning_variable)
                list_tam = [type_variable,variable,meaning_variable]
                list_struct_tam.append(list_tam.copy())

    def read_variable(self):
        # self.Variable_4_3 = Variable(self.path_file_C).read_variable()
        list_const = ['HCSHORT', 'HCLONG', 'CULONG', 'CSHORT', 'HCUSHORT', 'HCULONG', 'CUSHORT', 'HCUCHAR', 'CFLOAT', 'CFLAG', 'CCHAR', 'HCCHAR', 'HCFLAG', 'CLONG', 'CUCHAR']
        for variable in Variable(self.path_file_C).read_variable_all():
            if self.check_const_variable(variable[4],list_const):
                self.Constant_4_4.append(variable)
            else:
                self.Variable_4_3.append(variable)

    def read_typedef(self):
        read_file_C = self.source_code
        read_file_C = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",read_file_C)
        typerdef_ = re.findall("typedef.+;",read_file_C)
        list_tydef_struct = []
        list_tydef_enum = []
        list_default_type = []
        list_default_type_CONST = []
        for type in typerdef_:
            name_type = re.search("([\w]+);",type)
            if name_type != None:
                if type.find("const") != -1:
                    list_default_type_CONST.append(name_type.group(1))
                    # print("Const--",name_type.group(1))
                else:
                    list_default_type.append(name_type.group(1))
                    # print("No Const--",name_type.group(1))
        tydef_struct = self.read_typedef_struct()
        tydef_enum = self.read_typef_enum()
        for data in tydef_struct:
            tydef = list(data.keys())
            if tydef[0][1] == "Typerdef_struct-None":
                list_tydef_struct.append(tydef[0][2])
            else:
                list_tydef_struct.append(tydef[0][1])

        for data in tydef_enum:
            _tydef = list(data.keys())
            if _tydef[0][1] == "Typerdef_enum-None":
                list_tydef_enum.append(_tydef[0][2])
            else:
                list_tydef_enum.append(_tydef[0][1])
        # print(list_tydef_struct,list_tydef_enum,list_default_type,list_default_type_CONST)
        ##### dùng để lưu các định nghĩa const trong source 
        Typerdef.Type_const.extend(list_default_type_CONST.copy())
        Typerdef.Type_defaulted.extend(list_default_type.copy())
        return  list_tydef_struct,list_tydef_enum,list_default_type,list_default_type_CONST

    def check_const_variable(self, string, list_const = []):
        for _const in list_const:
            if string.find(_const) != -1 or string.find("const") != -1:
                return 1
        return 0

# end class Typerdef()

class Variable:
    def __init__(self,link_code) -> None:
        self.link_code = link_code
        self.__ctags = "ctags --fields=+ne -o - --sort=no  --c-types=v "
        self.Ctags = self.__ctags + '"' + self.link_code + '"'
        self.all_variable = []

    def cmd_and_read(self,command):
        # try:
        #     return os.popen(command).read()
        # except:
        #     subprocessx = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        #     subprocess_return = subprocessx.stdout.read()
        #     encoding = 'utf-8'
        #     info = subprocess_return.decode(encoding,errors="ignore")
        #     f = open('data_variable.txt', 'w',errors="ignore")
        #     f.write(info)
        #     f.close()
        #     f = open('data_variable.txt', 'r',errors="ignore")
        #     info = f.read()
        #     f.close()
        #     return info
        os.popen(command + ' >> data_variable.txt').read()
        f = open('data_variable.txt', 'r',encoding= "shift-jis",errors="ignore")
        info = f.read()
        f.close()
        os.remove("data_variable.txt")
        return info
        
    def read_variable_all(self):
        read_cmd_variable = self.cmd_and_read(self.Ctags)
        variable_tam = read_cmd_variable.replace(self.link_code.replace("\\","\\\\"),"")
        variable_tam = variable_tam.split("\n")
        for data in variable_tam:
            if re.search("[\w]+",data) == None:
                continue
            self.all_variable.append(self.conver_variable(data))
        return self.all_variable

    def conver_variable(self,string_variable):
        string_variable = string_variable.replace("volatile","")
        name_variavle = re.search("[\w]+",string_variable).group()
        try:
            typef_variable = re.search("typeref:typename:(.+)",string_variable).group(1)
        except:
            typef_variable = re.search("typeref:(.+)",string_variable).group(1)
        typef_variable = re.sub("\s*file:","",typef_variable).replace(":"," ")
        read_all_define_variale = re.search("\/\^(.+)\s+v",string_variable).group(1).replace("\\","")
        
        meaning_variable_tam = re.search("\/\*+([\s\S]*?)\*+\/|\/\/(.*)",read_all_define_variale)
        meaning_variable = "Meaning_variable-None"
        if meaning_variable_tam:
            try:
                meaning_variable = meaning_variable_tam.group(1).strip()
            except:
                meaning_variable = meaning_variable_tam.group(2).strip()

        name_variavle_2 = re.sub(";.*","",read_all_define_variale)
        name_variavle_2 = re.sub("=.+","",name_variavle_2)
        if name_variavle_2.find("[") != -1 and name_variavle_2.find("]") != -1:
            name_variavle_2 = re.search("[\w]+\s*\[.+",name_variavle_2).group()
        else:
            name_variavle_2 = re.split("\s+",name_variavle_2)[-1]

        # print(name_variavle, typef_variable, meaning_variable, name_variavle_2)

        return [name_variavle, typef_variable, meaning_variable, name_variavle_2, read_all_define_variale]


# end class variable()

# class DD(Class_Word._Word):
#     def __init__(self,link_word) -> None:
#         super().__init__(link_word)


### end class _word




if __name__ == '__main__':


    # links_source = r"C:\Projects\PMAS\PMA-15-RE\PMA-15-RE"
    # links = r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)\forCUSTOMER\NidecSWC_Lib\nidec_lib\PF\MDL\CDD\CurrentControl\fi_pwm_invadj_pe1.c"
    # # links = r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)\forCUSTOMER\NidecSWC_Lib\nidec_lib\CTRL\APL\PeDerating\derating.c"
    # Data = Typerdef(links)
    # # Data.read_define()
    # # Data.read_variable()
    # # Data.read_typef_enum()

    # Data.read_typedef_struct()
    # 

    # # Data.read_typedef_struct()
    # # Data.read_typef_enum()
    # # Data.read_define()
    # # print(Data.Variable_4_3)
    # # variable = Variable(r"C:\Projects\Schaeffler_Phase_2\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL20.00.00(SVAxX20TH-21909A)\forNIDEC\0_Src\PF\MDL\IF\if_mdl.h")
    # # variable.read_variable()
    # print(Typerdef.Type_const)

    #### test đọc hết kiểu const
    # list_data_define = []
    # links_source = r"C:\Projects\PMAS\PMA-15-RE\PMA-15-RE"
    # All_file_code = Export_file(links_source)
    # for File in All_file_code.List_All_file:
    #     print(File)
    #     Data = Typerdef(File)
    #     # Data.read_typedef()
    #     list_data_define.extend(Data.read_define())
    # print(list(set(Typerdef.Type_const)))
    # exxcel = write_excel("Database.xlsx")
    # exxcel.write("Define",list_data_define)
    # exxcel.save()

    ##########################end test đọc hết kiểu const

    ##########test luu typdef struct enum

    # list_data_define = []
    # links_source = r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)\forCUSTOMER"
    # All_file_code = Export_file(links_source)
    # for File in All_file_code.List_All_file:
    #     # print(File)
    #     Data = Typerdef(File)
    #     Data.read_typedef()
    # print(list(set(Typerdef.Type_const)))
    # result = dict(Typerdef.Typedef_struct, **Typerdef.Typedef_enum)
    # save_file_json("test.json",Typerdef.Typedef_file_enum)\


    links = r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)\forNIDEC\0_Src\CTRL\APL\Safety\MOTC_RE\redundant_estimate.c"
    Data = Typerdef(links)
    Data.read_variable()