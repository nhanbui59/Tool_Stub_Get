'''
Created on May 27, 2022

@author: nhanbuivan
'''
from os import pipe, truncate
from tkinter import *
from tkinter import filedialog
import tkinter
from docx import Document
import re
import json
import os
"""thư viện cần để gom paragraph và bảng(table) """
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

import mReadDataQANFix
import Class_write_excel

class SS4_Docx:
    data = {
            "enum": {},
            "struct": {},
            "variable": {},
            "const": {},
            "macro": {},
            }
    def __init__(self,file_path):
        self.word = Document(file_path)
        self.name_file = file_path.replace("/","\\").split("\\")[-1].split(".")[0]
        self.name_file = re.search("\((.+)\)",self.name_file).group(1)
        self.nameType = ["enum", "struct", "variable", "const", "macro"]

    """Đọc đoạn test bất kỳ có thuộc tính paragraphs bỏ qua được trackchange"""
    @staticmethod
    def convert_paragraphs_2_text(paragraph,all_text = True):
        rs = paragraph._element.xpath('.//w:t')
        if all_text != True:
            string = ""
            for i in range(len(rs)-1):
                if i > 0:
                    string += rs[i].text
            return string
        else:
            return u"".join([r.text for r in rs])
        return None # không thể xảy ra :) 

    @staticmethod
    def convert_all_paragraphs_2_text(paragraph):
        rs = paragraph._element.xpath('.//w:t')
        return u"".join([r.text for r in rs])

    """inter gom tuần tự paragraph->table theo thứ tự trong word"""
    @staticmethod
    def iter_block_items(object):
        object_ = object
        if isinstance(object_, _Document):
            parent_elm = object_.element.body
        elif isinstance(object_, _Cell):
            parent_elm = object_._tc
        else:
            raise ValueError("Có gì đó không đúng")

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, object_)
            elif isinstance(child, CT_Tbl):
                yield Table(child, object_)

    """bỏ các cell trùng nhau"""
    @staticmethod
    def iter_unique_cells(row):
        prior_tc = None
        for cell in row.cells:
            this_tc = cell._tc
            if this_tc is prior_tc:
                continue
            prior_tc = this_tc
            yield cell

    def cellPos(self,row, pos):
        return row.cells[pos]

    def detectDataInRow(self, row, stringIgnore):
        for cell in self.iter_unique_cells(row):
            string = self.convert_all_paragraphs_2_text(cell)
            if string == "":
                continue
            if string.strip() != stringIgnore:
                return string
        return ""
    
    def readTableEnum(self, table, stringMeaning):
        stringTable = "enum"
        stringTypeDef = ""
        for row in table.rows:
            if len(row.cells) < 1:
                continue 
            string = self.convert_all_paragraphs_2_text(self.cellPos(row, 0)).strip()
            if string == "列挙体名称":
                stringTypeDef = self.detectDataInRow(row, "列挙体名称")
                if stringTypeDef not in SS4_Docx.data[stringTable]:
                    SS4_Docx.data[stringTable][stringTypeDef] = []
                    SS4_Docx.data[stringTable][stringTypeDef].append(["-", stringMeaning])
            elif string  == "列挙体型":
                string = self.detectDataInRow(row, "列挙体型")
                if string not in SS4_Docx.data[stringTable]:
                    SS4_Docx.data[stringTable][string] = [["-", stringMeaning]]
            elif string == "メンバー":
                listTam = []
                for cell in self.iter_unique_cells(row):
                    string = self.convert_all_paragraphs_2_text(cell)
                    string = re.sub("\(\s*※\s*\d+\s*\)","",string).strip()
                    if string != "メンバー" and string != "ラベル名" and string != "値" and string != "データ内容":
                        listTam.append(string)
                if len(listTam) > 0:
                    SS4_Docx.data[stringTable][stringTypeDef].append([listTam[0], listTam[2]])
           
    def readTableStruct(self, table, stringMeaning):
        stringTable = "struct"
        stringTypeDef = ""
        for row in table.rows:
            if len(row.cells) < 1:
                continue 
            string = self.convert_all_paragraphs_2_text(self.cellPos(row, 0)).strip()
            if string == "構造体名称":
                stringTypeDef = self.detectDataInRow(row, "構造体名称")
                if stringTypeDef not in SS4_Docx.data[stringTable]:
                    SS4_Docx.data[stringTable][stringTypeDef] = []
                    SS4_Docx.data[stringTable][stringTypeDef].append(["-", stringMeaning])
            elif string  == "構造体型":
                string = self.detectDataInRow(row, "構造体型")
                if string not in SS4_Docx.data[stringTable]:
                    SS4_Docx.data[stringTable][string] = [["-", stringMeaning]]
            elif string == "メンバー":
                listTam = []
                for cell in self.iter_unique_cells(row):
                    string = self.convert_all_paragraphs_2_text(cell)
                    string = re.sub("\(\s*※\s*\d+\s*\)","",string)
                    string = re.sub("\*+","",string).strip()
                    if string != "メンバー" and string != "型" and string != "ラベル" and string != "データ内容":
                        listTam.append(string)
                if len(listTam) > 0:
                    SS4_Docx.data[stringTable][stringTypeDef].append(listTam[1:])
        
    def readTableVariable(self, table, stringMeaning):
        stringTable = "variable"
        stringTypeDef = ""
        listTam = ["", "", stringMeaning]
        for row in table.rows:
            if len(row.cells) < 1:
                continue 
            string = self.convert_all_paragraphs_2_text(self.cellPos(row, 0)).strip()
            if string == "名称":
                stringTypeDef = self.detectDataInRow(row, "名称")
                stringTypeDef = re.sub("\s+", "", stringTypeDef)
                if stringTypeDef not in SS4_Docx.data[stringTable]:
                    SS4_Docx.data[stringTable][stringTypeDef] = []
            elif string  == "範囲":
                string = self.detectDataInRow(row, "範囲")
                listTam[0] = string
            elif string == "LSB":
                string = self.detectDataInRow(row, "LSB")
                listTam[1] = string
        if stringTypeDef != "":
            SS4_Docx.data[stringTable][stringTypeDef] = listTam.copy()

    def readTableConst(self, table, stringMeaning):
        stringTable = "const"
        stringTypeDef = ""
        for row in table.rows:
            if len(row.cells) < 1:
                continue 
            string = self.convert_all_paragraphs_2_text(self.cellPos(row, 0)).strip()
            if string == "名称":
                stringTypeDef = self.detectDataInRow(row, "名称")
                stringTypeDef = re.sub("\s+", "", stringTypeDef)
                if stringTypeDef not in SS4_Docx.data[stringTable]:
                    SS4_Docx.data[stringTable][stringTypeDef] = []
        if stringTypeDef != "":
            SS4_Docx.data[stringTable][stringTypeDef] = [stringMeaning]
                                              
    def read_Data_table_definition(self):
        string = ""
        string_meaning = ""
        string_pos = ""
        read = False

        for block in self.iter_block_items(self.word):
            if isinstance(block, Paragraph):
                string = self.convert_all_paragraphs_2_text(block)
                if string == "":
                    continue
                else: 
                    string_meaning = string
                if block.style.name == 'Heading 2':
                    if string.find("Enumeration definition") != -1 :
                        read = True
                        string_pos = "Enumeration"
                    elif string.find("Structure definition") != -1:
                        string_pos = "Structure"
                    elif string.find("Global variable definition") != -1:
                        string_pos = "Global"
                    elif string.find("Constant definition") != -1:
                        string_pos = "Constant"
                    elif string.find("Macro definition") != -1:
                        string_pos = "Macro"
                elif string.find("Function definition") != -1 and block.style.name == 'Heading 1':
                    read = False

            elif isinstance(block, Table):
                if read == True:
                    string_meaning = re.sub("\(\s*※\s*\d+\s*\)","",string_meaning)

                    if string_pos == "Enumeration":
                        self.readTableEnum(block, string_meaning)
                    elif string_pos == "Structure":
                        self.readTableStruct(block, string_meaning)
                    elif string_pos == "Global":
                        self.readTableVariable(block, string_meaning)
                    elif string_pos == "Constant":
                        self.readTableConst(block, string_meaning)
                    # elif string_pos == "Macro":
                    #     list_data[4].append(list_data_tam.copy())
                    
    def runCMDNread(self,command):
        return os.popen(command).read()
    def acceptAllChange(self, path):
        file_path = path.replace("/","\\")
        file_path = self.runCMDNread("Accept_all_change.exe " + '"' + file_path + '"')
        return file_path


def fixDatabaseINOUT_FromDD(linkFolder):
    allFile = mReadDataQANFix.Class_read_links_file.Export_file(linkFolder)
    allFile.pattern_file = ".+\.docx" # xuất tất cả các file excel
    
    # print("Waiting accept changes!!!")
    # for file in allFile.List_All_file:
    #     docx = SS4_Docx(file)
    #     print(docx.acceptAllChange(file))
    # print("Accept changes complete !!!")
    
    print("Waiting fix database !!!")
    for file in allFile.List_All_file:
        docx = SS4_Docx(file)
        docx.read_Data_table_definition()
        print(file)

    # print(len(docx.data["enum"]))
    # print(len(docx.data["struct"]))
    # print(len(docx.data["variable"]))
    # print(len(docx.data["const"]))
          
    dataFileStruct = Class_write_excel.read_file_json(".\\Database\\Database_DDIO_struct.json")
    dataFileEnum = Class_write_excel.read_file_json(".\\Database\\Database_DDIO_enum.json")
    dataFileVariable = Class_write_excel.read_file_json(".\\Database\\Database_DDIO_variable.json")
    dataFileConst = Class_write_excel.read_file_json(".\\Database\\Database_DDIO_const.json")
    
    mReadDataQANFix.fixDatabase_InoutDD_FormQA(SS4_Docx.data["struct"], dataFileStruct, "struct")
    mReadDataQANFix.fixDatabase_InoutDD_FormQA(SS4_Docx.data["enum"], dataFileEnum, "enum")
    mReadDataQANFix.fixDatabase_InoutDD_FormQA(SS4_Docx.data["variable"], dataFileVariable, "variable")
    mReadDataQANFix.fixDatabase_InoutDD_FormQA(SS4_Docx.data["const"], dataFileConst, "const")
    
    print("Complete !!!")

def acceptTrackchange(linkFolder):
    allFile = mReadDataQANFix.Class_read_links_file.Export_file(linkFolder)
    allFile.pattern_file = ".+\.docx" # xuất tất cả các file excel
    
    print("Waiting accept changes!!!")
    for file in allFile.List_All_file:
        docx = SS4_Docx(file)
        print(docx.acceptAllChange(file))
    print("Accept changes complete !!!")

if __name__ == '__main__':
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    docx = SS4_Docx(file_path)
    docx.read_Data_table_definition()
    print(docx.data["enum"])

    # allFile = mReadDataQANFix.Class_read_links_file.Export_file(r"C:\Projects\Schaeffler_Phase_6\01_Working\05_Output_DD\01_DesignDocument")
    # allFile.pattern_file = ".+\.docx" # xuất tất cả các file excel
    # for file in allFile.List_All_file:
    #     docx = SS4_Docx(file)
    #     print(docx.acceptAllChange(file))
    #
    # for file in allFile.List_All_file:
    #     docx = SS4_Docx(file)
    #     docx.read_Data_table_definition()
    #     print(file)
    # print(len(docx.data["enum"]))
    # print(len(docx.data["struct"]))
    # print(len(docx.data["variable"]))
    # print(len(docx.data["const"]))
    # fixDatabaseINOUT_FromDD(r"C:\Projects\Schaeffler_Phase_6\01_Working\05_Output_DD\01_DesignDocument")
    # print("Complete !!!")

