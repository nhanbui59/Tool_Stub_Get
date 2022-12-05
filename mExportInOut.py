'''
Created on May 26, 2022

@author: nhanbuivan
'''
import re
from Class_Stub import *
import Class_Stub
import Class_inert_DD
import xlwings

g_Dic_all_init_source = Class_Stub.read_file_json(".\\Database\\Database_init_function.json")
g_Dic_function_in_file = Class_Stub.read_file_json(".\\Database\\Database_function_in_file.json")
dataFileStruct = Class_Stub.read_file_json(".\\Database\\Database_DDIO_struct.json")
dataFileEnum = Class_Stub.read_file_json(".\\Database\\Database_DDIO_enum.json")
dataFileVariable = Class_Stub.read_file_json(".\\Database\\Database_DDIO_variable.json")
dataFileConst = Class_Stub.read_file_json(".\\Database\\Database_DDIO_const.json")
dataFileFunction = Class_Stub.read_file_json(".\\Database\\Database_DDIO_Function.json")

def countTabStartLine(string):
    try:
        return re.search("[\w]", string).start()
    except:
        return None
    
def checkInputIfForWhile(string, countTab,listCode)->bool:
    patternInNOutput = "([^\s]+)(?:\s*\|=|\s*\+=|\s*&=|\s*%=|\s*\/=|\s*\*=|\s*-=|\s*=)"
    listCodeTam = listCode.copy()
    listCodeTam.reverse()
    inoutCheck = True
    for lineCode in listCodeTam:
        stringLine = lineCode.strip()
        if stringLine == "":
            continue
        if stringLine.startswith("else if") or stringLine.replace("{","").replace("}","") == "else":
            if countTabStartLine(lineCode) < (countTab - 1):
                inoutCheck = False
            continue
        elif stringLine.startswith("if"):
            if countTabStartLine(lineCode) < (countTab - 1):
                inoutCheck = True
            continue
        matchInNOut = re.search(patternInNOutput,stringLine)
        if matchInNOut and inoutCheck:
            if matchInNOut.group(1) == string and countTabStartLine(lineCode) <= countTab:
                # print(countTabStartLine(lineCode) , countTab)
                # print(lineCode)
                return False
                
    return True

def detectString(string):
    patternContentINOUT = "[\w]+"
    listReturn = []
    listTypedef = ["void","VOID","ULONGLONG","SIZE_T","ULONG","USHORT","UCHAR","LONG","SHORT","CHAR","FLAG","BOOL","FLOAT"]
    listOperato = ["+","-","*","/","%","&&","||",">>","<<"]
    listStringInput = re.findall(patternContentINOUT, string)
    for input in listStringInput:
        if input in listTypedef or input in listOperato:
            continue
        elif input.isdigit():
            continue
        elif input.find("0x") != -1:
            continue
        if re.search("\d+[FL\.]", input):
            continue
        listReturn.append(input.replace("*", "").replace(",", "").replace(";", ""))
    return listReturn

def detectcharacterInput(string):
    patternContentINOUT = "[^\s{}\(\)]+"
    listReturn = []
    listTypedef = ["void","VOID","ULONGLONG","SIZE_T","ULONG","USHORT","UCHAR","LONG","SHORT","CHAR","FLAG","BOOL","FLOAT"]
    listOperato = ["+","-","*","/","%","&&","||",">>","<<","==",">","<","<=",">=","!=","="]
    listStringInput = re.findall(patternContentINOUT, string)
    for input in listStringInput:
        if input in listTypedef or input in listOperato:
            continue
        elif input.isdigit():
            continue
        elif input.find("0x") != -1:
            continue
        if re.search("^\d+[FL\.]|^\d+;", input):
            continue
        if re.search("\[.+\]", input):
            liststring2 = re.findall("\[(.+?)\]", input)
            for tam in  liststring2:
                listReturn.extend(detectString(tam))
            input = re.sub("\[.+?\]", "[]",input)
        listReturn.append(input.replace("*", "").replace(",", "").replace(";", ""))
    return listReturn

class InOutInFunc:
    def __init__(self, functionCode)->None:
        self.functionCode = functionCode
        self.functionCode2List = self.functionCode.split("\n")
        self.constList = ['HCSHORT', 'HCLONG', 'CULONG', 'CSHORT', 'HCUSHORT', 'HCULONG', 'CUSHORT', 'HCUCHAR', 'CFLOAT', 'CFLAG', 'CCHAR', 'HCCHAR', 'HCFLAG', 'CLONG', 'CUCHAR']
        self.variableSaticInFunct = {}
        self.meaningSariableSaticInFunct = []
        self.variableSaticConst = {}
        self.variableLocalInFunct = []
        self.lineStart = 2
        self.code2List = self.formatIf()
        self.localIsGlobal = {}
        self.readVariableDeclare()
        self.listOutputVariableNFunction = []
        self.listCallFunction = []
        self.listInput = []
        self.listInputCheckAgain = []
        self.listArgv = []
        self.name_function = ""
        self.readArgv(self.code2List[0])
        self.functionreturn = False
    def formatIf(self):
        """
        - Định dạng code các điều kiện if, else if mằm trên 1 hàng
        """
        read_file_C = self.functionCode
        read_file_C = read_file_C.replace("    ","\t")
        read_file_C = read_file_C.replace("   ","\t")
        read_file_C = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",read_file_C)
        lines = read_file_C.split("\n")
        listLinesCode = []
        string_tam = ""
        for line in lines:
            if line.startswith("#"):
                continue
            string_tam += self.convertAutosar2DefaultType(line)
            if string_tam.find("if") != -1 or string_tam.find("else if") != -1:
                if string_tam.count("(") == string_tam.count(")"):
                    listLinesCode.append(string_tam)
                else:
                    continue
            else:
                listLinesCode.append(string_tam)
            string_tam = ""
            
        ##### định dạng các con trỏ, mảng không có khoảng trắng ở giữa
        for i in range(len(listLinesCode)):
            listLinesCode[i] = self.formatLineCode(listLinesCode[i])
        return listLinesCode        
        
    def convertAutosar2DefaultType(self,string_autosar):
        """
        - chuyển các biến autosar thành về các biến có định dạng bình thường
        """
        pattern_autosar = "FUNC\s*\(.+?\)|P2FUNC\s*\(.+?\)|FUNC_P2VAR\s*\(.+?\)|FUNC_P2CONST\s*\(.+?\)|CONSTP2VAR\s*\(.+?\)|CONSTP2CONST\s*\(.+?\)|P2VAR\s*\(.+?\)|P2CONST\s*\(.+?\)|VAR\s*\(.+?\)|CONST\s*\(.+?\)"
        match = re.findall(pattern_autosar,string_autosar)
        for autosar in match:
            try:
                typedef_match = re.search("\((.+)\)",autosar).group(1).split(",")[0].strip()
            except:
                continue
            string_autosar = string_autosar.replace(autosar,typedef_match,1)
        return string_autosar 
       
    def detectMeaningFormComment(self, stringNameVariable):
        for stringLine in self.functionCode2List:
            if stringNameVariable in stringLine:
                string = stringLine
                break
        stringMeaning = ""
        meaningMatch1 = re.search("\/\*+([\s\S]*?)\*+\/", string)
        meaningMatch2 = re.search("\/\/+(.*)", string)
        if meaningMatch1:
            stringMeaning = meaningMatch1.group(1).strip()
        elif meaningMatch2:
            stringMeaning = meaningMatch2.group(1).strip()
        if re.search("\t\t+",stringMeaning):
            stringMeaning = re.sub("\t\t+.*", "", stringMeaning)
        return stringMeaning
    
    def formatLineCode(self,stringLineCode):
        """
        - Định dạng các con trỏ, mảng không có khoảng trắng
        """
        listPatternFix = []
        listReplace = []
        listPatternFix.append("\[\s*(?=[\w])")   # convert "["   left righ no backspace
        listReplace.append("[")
        listPatternFix.append("\s*\]")  # convert "]"   left righ no backspace
        listReplace.append("]")
        listPatternFix.append("\s*\[")
        listReplace.append("[")
        listPatternFix.append("\]\s+(?=\.|\-\>|\[)")
        listReplace.append("]")
        listPatternFix.append("\s+\-\>")
        listReplace.append("->")
        listPatternFix.append("\-\>\s+")
        listReplace.append("->")
        listPatternFix.append("\s+\.|\.\s+")
        listReplace.append(".")
        for pattern, replacei in zip(listPatternFix,listReplace):
            stringLineCode = re.sub(pattern, replacei, stringLineCode)
        format2 = re.findall("\[.+?\]", stringLineCode)
        format3 = []
        for i in format2:
            format3.append(re.sub("\s+", "", i))
        for i,j in zip(format2, format3):
            stringLineCode = stringLineCode.replace(i,j,1)
        return stringLineCode   
     
    def check_const_variable(self, string, list_const = []):
        for _const in list_const:
            if string.find(_const) != -1 or string.find("const") != -1:
                return 1
        return 0
    
    def readVariableDeclare(self):
        self.lineStart = 0
        countLine = 0
        patternDetectVariable = "[\w\*]+\s+[\w\*]+(?:\s*=.+)*;"
        for line in self.code2List:
            countLine += 1
            if line == "":
                continue
            stringLine = line.strip()
            if re.search(patternDetectVariable, stringLine):
                # self.lineStart = countLine
                if(stringLine.startswith("static")):
                    stringLine = re.sub("=.+;|\s*;","",stringLine.lstrip("static"))
                    stringTam = self.removePointer(re.split("\s+", stringLine.strip())[-1])
                    if self.check_const_variable(stringLine, self.constList):
                        self.variableSaticConst[stringTam] = self.detectMeaningFormComment(stringTam)
                    if stringTam not in self.variableSaticInFunct:
                        self.variableSaticInFunct[stringTam] = self.detectMeaningFormComment(stringTam)
                else:
                    stringLocalvariableIsGlobal = stringLine
                    stringLine = re.sub("=.+;|\s*;","",stringLine)
                    stringTam = self.removePointer(re.split("\s+", stringLine.strip())[-1])
                    if stringTam not in self.variableLocalInFunct:
                        self.variableLocalInFunct.append(stringTam)
                    if re.search("([\w]+)\s*=\s*&\s*([\w]+)",stringLocalvariableIsGlobal):
                        stringLocalvariableIsGlobal = re.findall("([\w]+)\s*=\s*&\s*([\w]+)", stringLocalvariableIsGlobal)
                        _local, _global = stringLocalvariableIsGlobal[0][0], stringLocalvariableIsGlobal[0][1]
                        self.localIsGlobal[_local] = _global
            if "return" in line:
                self.functionreturn = True
            if line[0] == "{":
                self.lineStart = countLine
        
    def readOutputNFunctCall(self):
        patternVariableOutput = "([^\s]+)(?:\s*\|=|\s*\+=|\s*&=|\s*%=|\s*\/=|\s*\*=|\s*-=|\s*=)"
        patternFunctionleOutput = "^\s+([^\s]+)\s*\(.+\)\s*;"
        patternFunctionleCall = "^\s+([^\s]+)\s*\(\s*\)\s*;"
        patternFunctionleCall_IfCfc = "(IfCfc_.+?)\s*\("
        patternPlusPlus = "\s*(.+)\s*(?:\+\+|\-\-)\s*;"
        for line in self.code2List[2::]:
            string = line
            stringStrip = line.strip()
            if stringStrip == "" or stringStrip.startswith("if") or stringStrip.startswith("else if") or stringStrip.startswith("for") or stringStrip.startswith("while"):
                continue
            matchOutputVariable = re.search(patternVariableOutput,string)
            matchOutputFunction = re.search(patternFunctionleOutput,string)
            matchCallFunction = re.search(patternFunctionleCall,string)
            matchCallFunction_IfCfc = re.search(patternFunctionleCall_IfCfc,string)
            matchPlusPlus = re.search(patternPlusPlus,string)
            if matchOutputVariable or matchOutputFunction:
                if matchOutputVariable:
                    string = matchOutputVariable.group(1)
                elif matchOutputFunction:
                    string = matchOutputFunction.group(1)
                if string.startswith("IfCfc_"):
                    if string not in self.listCallFunction:
                        self.listCallFunction.append(string)
                elif string not in self.listOutputVariableNFunction and string not in self.variableLocalInFunct:
                    self.listOutputVariableNFunction.append(string)
            if matchCallFunction:
                string = matchCallFunction.group(1)
                if string not in self.listCallFunction:
                    self.listCallFunction.append(string)
            elif matchCallFunction_IfCfc:
                string = matchCallFunction_IfCfc.group(1)
                if string not in self.listCallFunction:
                    self.listCallFunction.append(string)
            if matchPlusPlus:
                if matchPlusPlus.group(1) not in self.listOutputVariableNFunction:
                    self.listOutputVariableNFunction.append(matchPlusPlus.group(1).replace("(","").replace(")",""))
                    
    def readInput(self):
        patternHaveEqual = "=(.+);"
        patternFunctionOutput = "[\w]+\s*\((.+)\)"
        patternInNOutput = "([^\s]+)(?:\s*\|=|\s*\+=|\s*&=|\s*%=|\s*\/=|\s*\*=|\s*-=)"
        patternOutPutArray = "([^\s]+)(?:\s*=)"
        patternPlusPlus = "\s*(.+)\s*(?:\+\+|\-\-)\s*;"
        
        listCodeFunction = self.code2List
        listInputFalse = [] ######### bỏ qua các input sai
        for iLine  in range(len(listCodeFunction)):
            if iLine < 2:
                continue
            line = listCodeFunction[iLine]
            stringStrip = line.strip()
            if line.strip() == "":
                continue
            listCheckInput = []
            if stringStrip.startswith("if") or stringStrip.startswith("else if"):
                stringStrip = re.search("\((.+)\)",line).group(1)
                listCheckInput = detectcharacterInput(stringStrip)
            elif stringStrip.startswith("for"):
                stringStrip = re.search("\((.+)\)",line).group(1)
                listCheckInput = detectcharacterInput(stringStrip)
            elif stringStrip.startswith("while"):
                stringStrip = re.search("\((.+)\)",line).group(1)
                listCheckInput = detectcharacterInput(stringStrip)
        
            matchHaveEqual = re.search(patternHaveEqual,stringStrip)
            matchFunctionOutput = re.search(patternFunctionOutput,stringStrip)
            matchInNOut = re.search(patternInNOutput,stringStrip)
            matchOutPutArray = re.search(patternOutPutArray,stringStrip)
            matchPlusPlus = re.search(patternPlusPlus,stringStrip)
            if matchPlusPlus:
                listCheckInput.append(matchPlusPlus.group(1).replace("(","").replace(")",""))
            if matchHaveEqual:
                # print(matchHaveEqual.group(1))
                listCheckInput = detectcharacterInput(matchHaveEqual.group(1))
            elif matchFunctionOutput:
                # print(matchFunctionOutput.group(1))
                listCheckInput = detectcharacterInput(matchFunctionOutput.group(1))
            if matchInNOut:
                listTam = detectcharacterInput(matchInNOut.group(1))
                listCheckInput.extend(listTam.copy())
            if matchOutPutArray:
                if re.search("\[.+\]", matchOutPutArray.group(1)):
                    liststring2 = re.findall("\[(.+?)\]", matchOutPutArray.group(1))
                    for tam in  liststring2:
                        listCheckInput.extend(detectString(tam))
            
            for _input in listCheckInput:
                if (_input in Class_inert_DD._define_name and _input[0] != "&")  or _input in self.variableLocalInFunct:
                    continue
                if _input in self.listCallFunction:
                    continue
                if _input not in self.listInput and (_input in self.variableSaticConst or _input not in self.listOutputVariableNFunction):
                    self.listInput.append(_input)
                elif _input not in self.listInput and _input in self.listOutputVariableNFunction:
                    # print(_input, "-->", line)
                    # checkInputIfForWhile(_input,countTabStartLine(line),listCodeFunction[lineStart:iLine])
                    # print("------------------------------------------------------")
                    if _input not in self.listInputCheckAgain:
                        self.listInputCheckAgain.append(_input)
                    if _input in listInputFalse:
                        continue
                    if checkInputIfForWhile(_input,countTabStartLine(line),listCodeFunction[self.lineStart:iLine]):
                        self.listInput.append(_input)
                    else:
                        listInputFalse.append(_input)
    
    def readInOutput(self, filter = False):
        self.readOutputNFunctCall()
        self.readInput()
        
        ####filter output
        for i in range(len(self.listOutputVariableNFunction)):
            self.listOutputVariableNFunction[i] = re.sub("^\s*\(.*?\)","",self.listOutputVariableNFunction[i])
            self.listOutputVariableNFunction[i] = self.removePointer(re.sub("\[.*?\]", "[]", self.listOutputVariableNFunction[i]))
            if filter == True:
                for argv in self.listArgv:
                    if self.listOutputVariableNFunction[i].startswith(argv):
                        self.listOutputVariableNFunction[i] = ""
                # for vStatic in self.variableSaticInFunct:
                #     if self.listOutputVariableNFunction[i].startswith(vStatic):
                #         self.listOutputVariableNFunction[i] = ""
                for vStatic in self.variableSaticConst:
                    if self.listOutputVariableNFunction[i].startswith(vStatic):
                        self.listOutputVariableNFunction[i] = ""
                for vLocal in self.variableLocalInFunct:
                    if self.listOutputVariableNFunction[i].startswith(vLocal):
                        self.listOutputVariableNFunction[i] = "" 
                if self.listOutputVariableNFunction[i].startswith("return"):
                    self.listOutputVariableNFunction[i] = ""
                
        listTemp = self.listOutputVariableNFunction.copy()
        self.listOutputVariableNFunction = []
        for _ in listTemp:
            if (_ != "" and _ not in self.listOutputVariableNFunction):
                self.listOutputVariableNFunction.append(_)
        # self.listOutputVariableNFunction = [_ for _ in listTemp if (_ != "" and _ not in self.listOutputVariableNFunction)]            
        ####filter call functio
        for i in range(len(self.listCallFunction)):
            self.listCallFunction[i] = re.sub("^\s*\(.*?\)","",self.listCallFunction[i])
        ####filter input
        for i in range(len(self.listInput)):
            self.listInput[i] = re.sub("^\s*\(.*?\)","",self.listInput[i])
            self.listInput[i] = self.removePointer(re.sub("\[.*\]", "[]", self.listInput[i]))
            if filter == True:
                for argv in self.listArgv:
                    if self.listInput[i].startswith(argv):
                        self.listInput[i] = ""
                # for vStatic in self.variableSaticInFunct:
                #     if self.listInput[i].startswith(vStatic):
                #         self.listInput[i] = ""
                for vLocal in self.variableLocalInFunct:
                    if self.listInput[i].startswith(vLocal):
                        self.listInput[i] = "" 
        listTemp = self.listInput.copy()
        self.listInput = []
        for _ in listTemp:
            if (_ != "" and _ not in self.listInput):
                self.listInput.append(_)
        # self.listInput = [_ for _ in listTemp if (_ != "" and _ not in self.listInput)]

    def removePointer(self,string):
        if re.search("\w",string[0]) == None:
            return string[1::]
        else:
            return string
        
    def readArgv(self, string):
        string = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",string)
        string = string.replace("static","").replace("inline", "").strip() #xóa chữ static và inline trong hàm
        ## tách tên function và các argument
        pattern_name_and_argument = "([\S]+)\s*\((.*)\)"
        name_and_argument = re.findall(pattern_name_and_argument,string)
        self.name_function = name_and_argument[0][0].strip() ### tách tên
        argument_function = name_and_argument[0][1] ### tách argument
        
        check_null_or_void = argument_function.strip()
        if check_null_or_void == "" or check_null_or_void == "void" or check_null_or_void == "VOID":
            self.listArgv = []
        else:
            list_argument = check_null_or_void.split(",")
            for argument in list_argument:
                stringNameargv = self.removePointer(re.split("\s+", argument)[-1])
                self.listArgv.append(stringNameargv)
    
def resultInOutCheckWord(string, fileName, listFunctin = [], dicLocal2Global = {}, dicVariableStatic = {}, dicConstStatic = {}):
    
    fileName = re.sub("\..*","",fileName)
    
    string_interface = "インタフェース設計書[file_name]を参照"
    string_file = "SW詳細設計書[file_name]を参照"
    string_in_file = "グローバル変数定義を参照"
    string_in_file_Funct = "関数定義を参照"
    string_variable_in_function = "Static変数を参照"
    string_variableConst_in_function = "Static定数を参照"
    
    ListNotInterface = ["if_rtedef", "if_cfc","if_cfc_hrp","if_cfc_hfk","if_mdl_setting_MOT"]
    
    listResult = ["", "", ""]
    listString = re.split("\-\>|\.",string)
    for i in range(len(listString)):
        istring = listString[i]
        if i == 0:
            if istring in Class_inert_DD._define_name and istring not in dicLocal2Global.values():
                return None
            elif istring in listFunctin:  ############ check is function
                filenameSubFunction = g_Dic_function_in_file.get(istring, "file_name.c")[0]
                filenameSubFunction = re.sub("\..*","",filenameSubFunction)
                if fileName == filenameSubFunction:
                    listResult[2] = string_in_file_Funct
                else:
                    if filenameSubFunction.startswith("if_") and filenameSubFunction not in ListNotInterface:
                        listResult[2] = string_interface.replace("file_name", filenameSubFunction.replace("if_","").upper())
                    else:
                        listResult[2] = string_file.replace("file_name", filenameSubFunction)
                listResult[0] = dataFileFunction.get(istring, istring)[0]
                listResult[1] = istring
                # print(listResult)
            elif istring in Class_inert_DD._define_name:  ###### check is macro
                index = Class_inert_DD._define_name.index(istring)
                listResult[0] = Class_inert_DD._define_meaning[index]
                listResult[1] = istring
                listResult[2] = re.sub("file_name", re.split("\.",Class_inert_DD._define_file[index])[0], string_file)
                # print(listResult)
            elif istring in dataFileStruct or istring in dataFileEnum:
                if istring in dataFileStruct:
                    dic = dataFileStruct
                else:
                    dic = dataFileEnum
                filenameSubFunction = dic.get(istring, "file_name.c")[1]
                filenameSubFunction = re.sub("\..*","",filenameSubFunction)
                if fileName == filenameSubFunction:
                    listResult[2] = string_in_file
                else:
                    if filenameSubFunction.startswith("if_") and filenameSubFunction not in ListNotInterface:
                        listResult[2] = string_interface.replace("file_name", filenameSubFunction.replace("if_","").upper())
                    else:
                        listResult[2] = string_file.replace("file_name", filenameSubFunction)
                listResult[0] = dic.get(istring, istring)[0]
                listResult[1] = istring
                # print(listResult)
            elif istring in dataFileVariable or istring in dataFileConst:
                if istring in dataFileVariable:
                    dic = dataFileVariable
                else:
                    dic = dataFileConst
                filenameSubFunction = dic.get(istring, "file_name.c")[7]
                filenameSubFunction = re.sub("\..*","",filenameSubFunction)
                if fileName == filenameSubFunction:
                    listResult[2] = string_in_file
                else:
                    if filenameSubFunction.startswith("if_") and filenameSubFunction not in ListNotInterface:
                        listResult[2] = string_interface.replace("file_name", filenameSubFunction.replace("if_","").upper())
                    else:
                        listResult[2] = string_file.replace("file_name", filenameSubFunction)
                listResult[0] = dic.get(istring, istring)[0]
                listResult[1] = istring
                # print(listResult)
            elif istring in dicConstStatic:
                listResult[0] = dicVariableStatic.get(istring, istring)
                listResult[1] = istring
                listResult[2] = string_variableConst_in_function
            elif istring in dicVariableStatic:
                listResult[0] = dicVariableStatic.get(istring, istring)
                listResult[1] = istring
                listResult[2] = string_variable_in_function
            else:
                listResult[0] = listResult[1] = istring
                listResult[2] = string_file = "SW詳細設計書[file_name]を参照"
            listResult[0] = istring if listResult[0].endswith("-None") else listResult[0]
        else:
            add = True
            if istring in dataFileStruct:
                dic = dataFileStruct
            elif istring in dataFileEnum:
                dic = dataFileEnum
            elif istring in dataFileVariable:
                dic = dataFileVariable
            elif istring in dataFileConst:
                dic = dataFileConst
            else:
                add = False
                listResult[0] += "." + istring
                listResult[1] += "." + istring
            if add == True:
                meaning = dic.get(istring, istring)[0]
                meaning = istring if meaning.endswith("-None") else meaning
                listResult[0] += "." + meaning
                listResult[1] += "." + istring
    return listResult

def exportRangeVariable(string):
    result = re.findall("[\dxA-F\+\.]+", string)
    if len(result) == 2:
        if string[0] == "-":
            result[0] = "-" + result[0]
        return result
    return []
            
def resultInOutCheckExcel(string, listCheckIntput = [], listAgrv = [], dicLocal2Global = {}, dicVariableStatic = {}, output = True):
    
    listResult = ["" for i in range(13)]
    listNone = ["" for i in range(13)]
    listString = re.split("\-\>|\.",string)
    if len(listString) == 1:
        istring  = listString[0]
        listResult[0] = istring
        if istring in listAgrv or istring in dicVariableStatic:
            listResult[0] = "@" + listResult[0]
            listResult[1] = dicVariableStatic.get(istring, "")
            listResult[7] = "Local"
        elif istring in dataFileVariable:
            listResult[1] = dataFileVariable.get(istring,"")[0]
            listResult[2] = dataFileVariable.get(istring,"")[2]
            listResult[5] = dataFileVariable.get(istring,"")[4]
            listResult[7] = dataFileVariable.get(istring,"")[6]
            rangeVariable = exportRangeVariable(dataFileVariable.get(istring,"")[3])
            if len(rangeVariable) == 2 and istring in listCheckIntput:
                listResult[3] = rangeVariable[0]
                listResult[4] = rangeVariable[1]
        else:
            return None
    else:
  
        for i in range(len(listString)):
            istring = listString[i]
            if i == 0:
                listResult[0] = istring
                if istring in listAgrv or istring in dicVariableStatic:
                    listResult[0] = "@" + listResult[0]
                    listResult[1] = dicVariableStatic.get(istring, "")
                    listResult[7] = "Local"
                elif istring in dataFileVariable:
                    listResult[1] = dataFileVariable.get(istring, listNone)[0]
                    listResult[5] = dataFileVariable.get(istring, listNone)[4]
                    listResult[7] = dataFileVariable.get(istring, listNone)[6]
                    rangeVariable = exportRangeVariable(dataFileVariable.get(istring, listNone)[3])
                    if len(rangeVariable) == 2 and istring in listCheckIntput:
                        listResult[3] = rangeVariable[0]
                        listResult[4] = rangeVariable[1]
                elif istring in dicLocal2Global:
                    listResult[0] = dicLocal2Global[istring]
                    listResult[1] = istring
                    listResult[7] = "Local"
                else:
                    return None
            else:
                add = True
                if istring in dataFileStruct:
                    dic = dataFileStruct
                else:
                    add = False
                    listResult[0] += "." + istring
                    listResult[1] += "." + istring
                if add == True:
                    meaning = dic.get(istring, istring)[0]
                    meaning = istring if meaning.endswith("-None") else meaning
                    listResult[0] += "." + istring
                    if istring == "U":
                        listResult[1] += ".brief Unsigned access"
                    elif istring == "B":
                        listResult[1] += ".brief Bitfield access"
                    elif istring == "I":
                        listResult[1] += ".brief Signed access"
                    else:
                        listResult[1] += "." + meaning
                if istring == listString[-1]:
                    if istring == "U":
                        listResult[2] = "UINT"
                    elif istring == "B":
                        listResult[2] = "UINT"
                    elif istring == "I":
                        listResult[2] = "INT"
                    else:
                        listResult[2] = dic.get(istring, listNone)[2]
                
    if string not in listCheckIntput or output == True:
        listResult[10] = "○"
        listResult[12] = "○"
    listResult[6] = "-"
    listResult[8] = "×"
    listResult[9] = "○"
    listResult[11] = "○"       
    return listResult



def exportInOutDocx(functionname, stringCode):
    try:
        _test = Class_Stub._Function(g_Dic_function_in_file[functionname][1])
    except:
        print(functionname + " Not exits !!!!")
        return
    
    if stringCode == None:
        _sub_function = _test.get_sub_function(_test.Get_function(functionname))
        vTest = InOutInFunc(_test.Get_function(functionname))
        print(_test.Get_function(functionname))
    else:
        _sub_function = _test.get_sub_function(stringCode)
        vTest = InOutInFunc(stringCode)
    print("-------------------------------------------------------------Result-----------------------------------------------------------------------------------")
     
    vTest.readInOutput(True)
    # print(vTest.variableLocalInFunct)
    # print(vTest.variableSaticInFunct)
    # print(vTest.listArgv)
    listINPUT = []
    for stringinput in vTest.listInput:
        listTrue = resultInOutCheckWord(stringinput, g_Dic_function_in_file[vTest.name_function][0], _sub_function, vTest.localIsGlobal, vTest.variableSaticInFunct, vTest.variableSaticConst)
        if listTrue != None:
            listINPUT.append(listTrue)
    
    listOUTPUT = []
    for stringinput in vTest.listOutputVariableNFunction:
        listTrue = resultInOutCheckWord(stringinput, g_Dic_function_in_file[vTest.name_function][0], _sub_function, vTest.localIsGlobal, vTest.variableSaticInFunct, vTest.variableSaticConst)
        if listTrue != None:
            listOUTPUT.append(listTrue)
    
    listFUNCTIONCALL = []
    for stringinput in vTest.listCallFunction:
        listTrue = resultInOutCheckWord(stringinput, g_Dic_function_in_file[vTest.name_function][0], _sub_function, vTest.localIsGlobal)
        if listTrue != None:
            listFUNCTIONCALL.append(listTrue)            
    
    workbook = xlwings.Book()
    worksheet = workbook.sheets[0]
    worksheet.range('B1').value = "INPUT"
    worksheet.range('B1').api.Font.Bold = True
    last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    worksheet.range(f"B{last_row}").value = listINPUT
    last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    worksheet.range(f"B{last_row}").value = "OUTPUT"
    worksheet.range(f"B{last_row}").api.Font.Bold = True
    last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    worksheet.range(f"B{last_row}").value = listOUTPUT
    last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    worksheet.range(f"B{last_row}").value = "CALL FUNCTION"
    worksheet.range(f"B{last_row}").api.Font.Bold = True
    last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    worksheet.range(f"B{last_row}").value = listFUNCTIONCALL
    worksheet.autofit()
    try:
        print()
        print("Check variable -> 'output' and 'input'")
        for inputcheckaganin in vTest.listInputCheckAgain:
            print(inputcheckaganin)
        print()
        print("Complete !!!")
    except:
        pass

def exportInOutExcel(functionname, stringCode, linkFileMap):
    try:
        _test = Class_Stub._Function(g_Dic_function_in_file[functionname][1])
    except:
        print(functionname + " Not exits !!!!")
        return
    
    if stringCode == None:
        _sub_function = _test.get_sub_function(_test.Get_function(functionname))
        stringCode = _test.Get_function(functionname)
        vTest = InOutInFunc(stringCode)
        print(stringCode)
    else:
        _sub_function = _test.get_sub_function(stringCode)
        vTest = InOutInFunc(stringCode)

    print("-------------------------------------------------------------Result-----------------------------------------------------------------------------------")
    vTest.readInOutput(False)

    # print("-----------------------input--------------------------")
    listALL = []
    for stringinput in vTest.listInput:
        if stringinput in Class_inert_DD._define_name or stringinput in dataFileConst or stringinput in vTest.variableSaticConst or stringinput in vTest.variableLocalInFunct:
            continue
        if stringinput in _sub_function or stringinput in vTest.listOutputVariableNFunction:
            continue
        # print(stringinput)
    
        listTrue = resultInOutCheckExcel(stringinput, vTest.listInput, vTest.listArgv, vTest.localIsGlobal, vTest.variableSaticInFunct, output=False)
        if listTrue != None:
            # print(listTrue)
            listALL.append(listTrue)
    
    # print("-----------------------output--------------------------")
    for stringinput in vTest.listOutputVariableNFunction:
        if stringinput in Class_inert_DD._define_name or stringinput in dataFileConst or stringinput in vTest.variableSaticConst or stringinput in vTest.variableLocalInFunct:
            continue
        if stringinput in _sub_function:
            continue
        listTrue = resultInOutCheckExcel(stringinput, vTest.listInput, vTest.listArgv, vTest.localIsGlobal, vTest.variableSaticInFunct)
        if listTrue != None:
            # print(listTrue)
            listALL.append(listTrue)
    
    with open(linkFileMap, "r", encoding="utf-8", errors="ignore") as fileMap:
        string_check_optimize = fileMap.read()
        fileMap.close()
    function = functionname
    data_stub = export_stub_for_IO_check_optimize(function, string_check_optimize,[],stringCode)
    for stub in data_stub:
        if stub == "\n":
            continue
        listResult = ["" for i in range(13)]
        if "@" in stub:
            listResult[0] = stub
            listResult[7] = "Local"
            if "@AMOUT_" in stub:
                listResult[3] = "-"
                listResult[4] = "-"
                listResult[5] = "-"
                listResult[6] = "-"
                listResult[10] = "○"
                listResult[12] = "○"
                listResult[6] = "-"
                listResult[8] = "×"
                listResult[9] = "○"
                listResult[11] = "○"
            else:
                listResult[6] = "-"
                listResult[8] = "×"
                listResult[9] = "○"
                listResult[11] = "○"
            listALL.append(listResult.copy())
        else:
            if stub in vTest.listOutputVariableNFunction or stub in vTest.listInput:
                continue
            listTrue = resultInOutCheckExcel(stub, vTest.listInput, vTest.listArgv, vTest.localIsGlobal, vTest.variableSaticInFunct, output=True)
            if listTrue != None:
                listALL.append(listTrue)
    for i in range(len(listALL)):
        listALL[i][0] = listALL[i][0].replace("[]","[0]")
    if vTest.functionreturn:
        listResult = ["" for i in range(13)]
        listResult[0] = vTest.name_function + "@@"
        listResult[3] = "-"
        listResult[4] = "-"
        listResult[5] = "-"
        listResult[6] = "-"
        listResult[10] = "○"
        listResult[12] = "○"
        listResult[6] = "-"
        listResult[8] = "×"
        listResult[7] = "Local"
        listALL.append()
    workbook = xlwings.Book()
    worksheet = workbook.sheets[0]
    worksheet.range(f"B1").value = listALL
    worksheet.autofit()
    try:
        print()
        print("Check variable -> 'output' and 'input'")
        for inputcheckaganin in vTest.listInputCheckAgain:
            print(inputcheckaganin)
        print()
        print("Complete !!!")
    except:
        pass
    
if __name__ == "__main__":

#     code = """VOID	Knl_Convert_Cycle_Tsg3( const UCHAR unit, const USHORT pwm_cycle, ULONG data_out[], ULONG* p_dead_tim_mcu )
# {
# 	ULONG	atom_cmp0;
# 	ULONG	dead_tim;
# 	ULONG	addelay_0;
# 	ULONG	addelay_2;

# 	if ( ( data_out != NULL ) && ( pwm_cycle != Z_ZERO ) )
# 	{
# 		atom_cmp0	= (ULONG)( ZPWM_CLK_10M / pwm_cycle );

# 		dead_tim = ZPWM_DEADTIME_DEFAULT_VALUE;

# 		addelay_0	= ( dead_tim + ZATOM_ADDELAY ) & ZADSMPL_MASK;	/* ｱｯﾌﾟｶｳﾝﾄ時ｺﾝﾍﾟｱﾏｯﾁ設定(DCMP0E:ﾃﾞｯﾄﾞﾀｲﾑ + ADｻﾝﾌﾟﾘﾝｸﾞﾃﾞｨﾚｲ)	*/
# 		addelay_2	= ( atom_cmp0 - ZATOM_ADDELAY ) & ZADSMPL_MASK;	/* ﾀﾞｳﾝｶｳﾝﾄ時ｺﾝﾍﾟｱﾏｯﾁ設定(DCMP2E:ｷｬﾘｱ周期 - ADｻﾝﾌﾟﾘﾝｸﾞﾃﾞｨﾚｲ)	*/

# 		/* 出力用周期ﾊﾞｯﾌｧへ代入 */
# 		/* Set to output cycle buffer */
# 		data_out[TABLE_0]			= atom_cmp0;
# 		data_out[TABLE_1]			= addelay_0;
# 		data_out[TABLE_2]			= addelay_2;

# 		*p_dead_tim_mcu			= dead_tim;						/* ﾃﾞｯﾄﾞﾀｲﾑMCU設定値 返却値設定				*/
# 	}
# 	else
# 	{
# 		/* 処理不要 */
# 		/* No processing required */
# 	}

# }"""
#     # linkFileMap = r"C:\Projects\Schaeffler_Phase_6\01_Working\01_INPUT\01_Source_Code\V1\06_Map_files\BL21.05.00(0bce1d9)_INLINE_OPTIMIZATION_OFF\Nidec_Lib_link_test.map"
#     exportInOutDocx("Knl_Convert_Cycle_Tsg3",code)

################## bộ test 1#############################
    stringCode = """VOID	Knl_Set_Mode_Tsg3( const UCHAR unit, const USHORT pwmreq, const USHORT pwmsts )
{
	ULONG	dtm_ctrl2_buff;
	/* GTM ﾓｼﾞｭｰﾙ ﾚｼﾞｽﾀ ﾎﾟｲﾝﾀｰ ｾｯﾄ */
	/* GTM Module register pointer Set */
    Ifx_GTM	*gtm = &MODULE_GTM;

	/*	┌───────────────┬───────────────────────────────┐	*/
	/*	│								│				PWM出力要求(pwmreq)								│	*/
	/*	│								├───────┬───────┬───────┬───────┤	*/
	/*	│								│FET全ｵﾌ		│全相PWMﾀｲﾏ出力│各FETｵﾝ操作	│2相PWMﾀｲﾏ出力	│	*/
	/*	├───────┬───────┼───────┼───────┼───────┼───────┤	*/
	/*	│PWM出力状態	│FET全ｵﾌ		│		―		│		①		│		②		│		③		│	*/
	/*	│(pwmsts)		├───────┼───────┼───────┼───────┼───────┤	*/
	/*	│				│PWMﾀｲﾏ出力	│		④		│		―		│		⑤		│		⑥		│	*/
	/*	│				├───────┼───────┼───────┼───────┼───────┤	*/
	/*	│				│各FETｵﾝ操作	│		⑦		│		⑧		│		―		│		⑨		│	*/
	/*	│				├───────┼───────┼───────┼───────┼───────┤	*/
	/*	│				│2相PWMﾀｲﾏ出力	│		⑩		│		⑪		│		⑫		│		―		│	*/
	/*	└───────┴───────┴───────┴───────┴───────┴───────┘	*/
	/*------------------------------------------------------------------------------------------------------*/
	/* 特記事項:																							*/
	/* 全相PWMﾀｲﾏ出力設定からの各FETｵﾝ操作設定時(⑤)、または、												*/
	/* 2相PWMﾀｲﾏ出力設定からの各FETｵﾝ操作設定時(⑫)、または、												*/
	/* 各FETｵﾝ操作設定からの全相PWMﾀｲﾏ出力設定時(⑧)、または、												*/
	/* 各FETｵﾝ操作設定からの2相PWMﾀｲﾏ出力設定時(⑨)の縦短絡を考慮し、										*/
	/* FETｵﾝ切替え時は全FETｵﾌ状態を経由する。																*/
	/*------------------------------------------------------------------------------------------------------*/
	if ( pwmsts != ZTSG3_ALLOFF ) 
	{
		if ( unit == ZTSG3_UNIT0 )
		{
			vulPWMPORT_STATUS[unit]					= ZCDTM0_DTM5_CH_CTRL2_ALLOFF;
			gtm->CDTM[unit].DTM[5].CTRL.B.UPD_MODE	= ZCDTMx_DTM5_CH_CTRL_UPD_ASYNC;
			gtm->CDTM[unit].DTM[5].CH_CTRL2.U		= ZCDTM0_DTM5_CH_CTRL2_ALLOFF;
			gtm->CDTM[unit].DTM[5].CH_CTRL2_SR.U	= ZCDTM0_DTM5_CH_CTRL2_ALLOFF;
		}
		else if ( unit == ZTSG3_UNIT1 )
		{
			vulPWMPORT_STATUS[unit]					= ZCDTM1_DTM5_CH_CTRL2_ALLOFF;
			gtm->CDTM[unit].DTM[5].CTRL.B.UPD_MODE	= ZCDTMx_DTM5_CH_CTRL_UPD_ASYNC;
			gtm->CDTM[unit].DTM[5].CH_CTRL2.U		= ZCDTM1_DTM5_CH_CTRL2_ALLOFF;
			gtm->CDTM[unit].DTM[5].CH_CTRL2_SR.U	= ZCDTM1_DTM5_CH_CTRL2_ALLOFF;
		}
		else
		{
			/* 処理なし */
		}
	}Nguyen Thi My Dung

	/*** 要求がFETをｵﾝ駆動する場合(①,②,③,⑤,⑥,⑧,⑨,⑪,⑫)、FETをｵﾝする ***/
	if ( pwmreq != ZTSG3_ALLOFF )
	{
		if ( pwmreq == ZTSG3_ALLPWM )						/* 全相PWMﾀｲﾏ出力指定							*/
		{
			if ( unit == ZTSG3_UNIT0 )
			{
				vulPWMPORT_STATUS[unit]						= ZCDTM0_DTM5_CH_CTRL2_PWMALL;
				gtm->CDTM[unit].DTM[5].CH_CTRL2_SR.U		= ZCDTM0_DTM5_CH_CTRL2_PWMALL;
			}
			else if ( unit == ZTSG3_UNIT1 )
			{
				vulPWMPORT_STATUS[unit]						= ZCDTM1_DTM5_CH_CTRL2_PWMALL;
				gtm->CDTM[unit].DTM[5].CH_CTRL2_SR.U		= ZCDTM1_DTM5_CH_CTRL2_PWMALL;
			}
			else
			{
				/* 処理なし */
			}
		}
		else												/* 相の上下段ごとに個別指定						*/
		{
			dtm_ctrl2_buff	= Z0;
			/** U相上側 **/
			if ( ( pwmreq & ZTSG3TO1_PWM ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PWMU_____;		/* U相上側 PWM出力				*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PWMU_____;		/* U相上側 PWM出力				*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else if ( ( pwmreq & ZTSG3TO1_PORT_ON ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORTU_____ON;	/* U相上側 PortON出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORTU_____ON;	/* U相上側 PortON出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORTU_____OFF;	/* U相上側 PortOFF出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORTU_____OFF;	/* U相上側 PortOFF出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}

			/** U相下側 **/
			if ( ( pwmreq & ZTSG3TO2_PWM ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PWM___U__;		/* U相下側 PWM出力				*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PWM___U__;		/* U相下側 PWM出力				*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else if ( ( pwmreq & ZTSG3TO2_PORT_ON ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT___U__ON;	/* U相下側 PortON出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT___U__ON;	/* U相下側 PortON出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT___U__OFF;	/* U相下側 PortOFF出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT___U__OFF;	/* U相下側 PortOFF出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}

			/** V相上側 **/
			if ( ( pwmreq & ZTSG3TO3_PWM ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PWM_V____;		/* V相上側 PWM出力				*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PWM_V____;		/* V相上側 PWM出力				*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else if ( ( pwmreq & ZTSG3TO3_PORT_ON ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT_V____ON;	/* V相上側 PortON出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT_V____ON;	/* V相上側 PortON出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT_V____OFF;	/* V相上側 PortOFF出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT_V____OFF;	/* V相上側 PortOFF出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}

			/** V相下側 **/
			if ( ( pwmreq & ZTSG3TO4_PWM ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PWM____V_;		/* V相下側 PWM出力				*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PWM____V_;		/* V相下側 PWM出力				*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else if ( ( pwmreq & ZTSG3TO4_PORT_ON ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT____V_ON;	/* V相下側 PortON出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT____V_ON;	/* V相下側 PortON出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT____V_OFF;	/* V相下側 PortOFF出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT____V_OFF;	/* V相下側 PortOFF出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}

			/** W相上側 **/
			if ( ( pwmreq & ZTSG3TO5_PWM ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PWM__W___;		/* W相上側 PWM出力				*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PWM__W___;		/* W相上側 PWM出力				*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else if ( ( pwmreq & ZTSG3TO5_PORT_ON ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT__W___ON;	/* W相上側 PortON出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT__W___ON;	/* W相上側 PortON出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT__W___OFF;	/* W相上側 PortOFF出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT__W___OFF;	/* W相上側 PortOFF出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}

			/** W相下側 **/
			if ( ( pwmreq & ZTSG3TO6_PWM ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PWM_____W;		/* W相下側 PWM出力				*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PWM_____W;		/* W相下側 PWM出力				*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else if ( ( pwmreq & ZTSG3TO6_PORT_ON ) != 0 )
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT_____WON;	/* W相下側 PortON出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT_____WON;	/* W相下側 PortON出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}
			else
			{
				if ( unit == ZTSG3_UNIT0 )
				{
					dtm_ctrl2_buff	|= ZCDTM0_DTM5_CH_CTRL2_PORT_____WOFF;	/* W相下側 PortOFF出力			*/
				}
				else if ( unit == ZTSG3_UNIT1 )
				{
					dtm_ctrl2_buff	|= ZCDTM1_DTM5_CH_CTRL2_PORT_____WOFF;	/* W相下側 PortOFF出力			*/
				}
				else
				{
					/* 処理なし */
				}
			}

			/********************************************************************/
			/* 特記事項：														*/
			/*	QAC Mandatory対応の一環で処理を追加。							*/
			/*	現状では設計上、elseに入ることはない為、"処理なし"で問題なし。	*/
			/********************************************************************/
			if( ( unit == ZTSG3_UNIT0 ) || ( unit == ZTSG3_UNIT1 ) )
			{
				vulPWMPORT_STATUS[unit]							= dtm_ctrl2_buff;
				gtm->CDTM[unit].DTM[5].CH_CTRL2_SR.U			= dtm_ctrl2_buff;
			}
			else
			{
				/*** 処理なし ***/
			}
		}
	}

	if ( unit == ZTSG3_UNIT0 )
	{
		gtm->CDTM[unit].DTM[5].CTRL.U 				= ZCDTM0_DTM5_CH_CTRL_INI;
	}
	else if ( unit == ZTSG3_UNIT1 )
	{
		gtm->CDTM[unit].DTM[5].CTRL.U 				= ZCDTM1_DTM5_CH_CTRL_INI;
	}
	else
	{
		/* 処理なし */
	}
}
"""

    vTest = InOutInFunc(stringCode)      
    vTest.readInOutput()
    print(vTest.variableLocalInFunct)
    print(vTest.variableSaticInFunct)
    print(vTest.listArgv)
    
    print("out------------------")
    for i in vTest.listOutputVariableNFunction:
        print(i)
    print("call------------------")
    for i in vTest.listCallFunction:
        print(i)
    print("in------------------")
    for i in vTest.listInput:
        print(i)
    
    print("Complete !!!")
########################################################       
################## bộ test 2#############################
    # g_Dic_all_init_source = Class_Stub.read_file_json(".\\Database\\Database_init_function.json")
    # g_Dic_function_in_file = Class_Stub.read_file_json(".\\Database\\Database_function_in_file.json")
    # dataFileStruct = Class_Stub.read_file_json(".\\Database\\Database_DDIO_struct.json")
    # dataFileEnum = Class_Stub.read_file_json(".\\Database\\Database_DDIO_enum.json")
    # dataFileVariable = Class_Stub.read_file_json(".\\Database\\Database_DDIO_variable.json")
    # dataFileConst = Class_Stub.read_file_json(".\\Database\\Database_DDIO_const.json")
    #
    # functionname = "Knl_Convert_Cycle_Tsg3"
    # _test = Class_Stub._Function(g_Dic_function_in_file[functionname][1])
    # # print(_test.Get_function(functionname))
    # _sub_function = _test.get_sub_function(_test.Get_function(functionname))
    # print(_sub_function)
    #
    # vTest = InOutInFunc(_test.Get_function(functionname))      
    # vTest.readInOutput(True)
    # print(vTest.variableLocalInFunct)
    # print(vTest.variableSaticInFunct)
    # print(vTest.listArgv)
    #
    # listINPUT = []
    # for stringinput in vTest.listInput:
    #     listTrue = resultInOutCheckWord(stringinput, g_Dic_function_in_file[vTest.name_function][0], _sub_function, vTest.localIsGlobal, vTest.variableSaticInFunct, vTest.variableSaticConst)
    #     if listTrue != None:
    #         listINPUT.append(listTrue)
    #
    # listOUTPUT = []
    # for stringinput in vTest.listOutputVariableNFunction:
    #     listTrue = resultInOutCheckWord(stringinput, g_Dic_function_in_file[vTest.name_function][0], _sub_function, vTest.localIsGlobal, vTest.variableSaticInFunct, vTest.variableSaticConst)
    #     if listTrue != None:
    #         listOUTPUT.append(listTrue)
    #
    # listFUNCTIONCALL = []
    # for stringinput in vTest.listCallFunction:
    #     listTrue = resultInOutCheckWord(stringinput, g_Dic_function_in_file[vTest.name_function][0], _sub_function, vTest.localIsGlobal)
    #     if listTrue != None:
    #         listFUNCTIONCALL.append(listTrue)            
    #
    # workbook = xlwings.Book()
    # worksheet = workbook.sheets[0]
    # worksheet.range('B1').value = "INPUT"
    # worksheet.range('B1').api.Font.Bold = True
    # last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    # worksheet.range(f"B{last_row}").value = listINPUT
    # last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    # worksheet.range(f"B{last_row}").value = "OUTPUT"
    # worksheet.range(f"B{last_row}").api.Font.Bold = True
    # last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    # worksheet.range(f"B{last_row}").value = listOUTPUT
    # last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    # worksheet.range(f"B{last_row}").value = "CALL FUNCTION"
    # worksheet.range(f"B{last_row}").api.Font.Bold = True
    # last_row = worksheet.range(f"B{worksheet.cells.last_cell.row}").end("up").row + 1
    # worksheet.range(f"B{last_row}").value = listFUNCTIONCALL
    # worksheet.autofit()
    #
    # print()
    # print("Các biến input này nên kiểm tra lại vì nó có vừa 'output' vừa 'input'")
    # for inputcheckaganin in vTest.listInputCheckAgain:
    #     print(inputcheckaganin)
    #
    # print()
    # print("Complete !!!")
######################################################## 
################# bộ test 3#############################
    # g_Dic_all_init_source = Class_Stub.read_file_json(".\\Database\\Database_init_function.json")
    # g_Dic_function_in_file = Class_Stub.read_file_json(".\\Database\\Database_function_in_file.json")
    # dataFileStruct = Class_Stub.read_file_json(".\\Database\\Database_DDIO_struct.json")
    # dataFileEnum = Class_Stub.read_file_json(".\\Database\\Database_DDIO_enum.json")
    # dataFileVariable = Class_Stub.read_file_json(".\\Database\\Database_DDIO_variable.json")
    # dataFileConst = Class_Stub.read_file_json(".\\Database\\Database_DDIO_const.json")
    #
    # functionname = "Knl_Init_DCDC_Dma"
    # _test = Class_Stub._Function(g_Dic_function_in_file[functionname][1])
    # # print(_test.Get_function(functionname))
    # _sub_function = _test.get_sub_function(_test.Get_function(functionname))
    # # print(_sub_function)
    #
    # vTest = InOutInFunc(_test.Get_function(functionname))      
    # vTest.readInOutput(False)
    # print("Variable local")
    # print(vTest.variableLocalInFunct)
    # print("Variable static in function")
    # print(vTest.variableSaticInFunct)
    # print("Variable local = macro")
    # print(vTest.localIsGlobal)
    # print("Argument")
    # print(vTest.listArgv)
    # # print(vTest.listInput)
    # # print(vTest.listOutputVariableNFunction)
    # print("Funtion name")
    # print(functionname)
    # # print("-----------------------input--------------------------")
    # listALL = []
    # for stringinput in vTest.listInput:
    #     if stringinput in Class_inert_DD._define_name or stringinput in dataFileConst or stringinput in vTest.variableSaticConst or stringinput in vTest.variableLocalInFunct:
    #         continue
    #     if stringinput in _sub_function or stringinput in vTest.listOutputVariableNFunction:
    #         continue
    #     # print(stringinput)
    #
    #     listTrue = resultInOutCheckExcel(stringinput, vTest.listInput, vTest.listArgv, vTest.localIsGlobal, vTest.variableSaticInFunct, output=False)
    #     if listTrue != None:
    #         # print(listTrue)
    #         listALL.append(listTrue)
    #
    # # print("-----------------------output--------------------------")
    # for stringinput in vTest.listOutputVariableNFunction:
    #     if stringinput in Class_inert_DD._define_name or stringinput in dataFileConst or stringinput in vTest.variableSaticConst or stringinput in vTest.variableLocalInFunct:
    #         continue
    #     if stringinput in _sub_function:
    #         continue
    #     listTrue = resultInOutCheckExcel(stringinput, vTest.listInput, vTest.listArgv, vTest.localIsGlobal, vTest.variableSaticInFunct)
    #     if listTrue != None:
    #         # print(listTrue)
    #         listALL.append(listTrue)
    #
    #
    # linkFileMap = r"C:\Projects\Schaeffler_Phase_6\01_Working\01_INPUT\01_Source_Code\V1\06_Map_files\BL21.05.00(0bce1d9)_INLINE_OPTIMIZATION_OFF\Nidec_Lib_link_test.map"
    # with open(linkFileMap, "r", encoding="utf-8", errors="ignore") as fileMap:
    #     string_check_optimize = fileMap.read()
    #     fileMap.close()
    # function = functionname
    # data_stub = export_stub_for_IO_check_optimize(function,string_check_optimize)
    # for stub in data_stub:
    #     if stub == "\n":
    #         continue
    #     listResult = ["" for i in range(13)]
    #     if "@" in stub:
    #         listResult[0] = stub
    #         listResult[7] = "Local"
    #         if "@AMOUT_" in stub:
    #             listResult[3] = "-"
    #             listResult[4] = "-"
    #             listResult[5] = "-"
    #             listResult[6] = "-"
    #             listResult[10] = "○"
    #             listResult[12] = "○"
    #             listResult[6] = "-"
    #             listResult[8] = "×"
    #             listResult[9] = "○"
    #             listResult[11] = "○"
    #         else:
    #             listResult[6] = "-"
    #             listResult[8] = "×"
    #             listResult[9] = "○"
    #             listResult[11] = "○"
    #         listALL.append(listResult.copy())
    #     else:
    #         if stub in vTest.listOutputVariableNFunction or stub in vTest.listInput:
    #             continue
    #         listTrue = resultInOutCheckExcel(stub, vTest.listInput, vTest.listArgv, vTest.localIsGlobal, vTest.variableSaticInFunct, output=True)
    #         if listTrue != None:
    #             print(listTrue)
    #             listALL.append(listTrue)
    # print("-----------------------ALL--------------------------")
    # for i in range(len(listALL)):
    #     listALL[i][0] = listALL[i][0].replace("[]","[0]")
    # if vTest.functionreturn:
    #     listResult = ["" for i in range(13)]
    #     listResult[0] = vTest.name_function + "@@"
    #     listResult[3] = "-"
    #     listResult[4] = "-"
    #     listResult[5] = "-"
    #     listResult[6] = "-"
    #     listResult[10] = "○"
    #     listResult[12] = "○"
    #     listResult[6] = "-"
    #     listResult[8] = "×"
    #     listResult[7] = "Local"
    #     listALL.append()
    # workbook = xlwings.Book()
    # worksheet = workbook.sheets[0]
    # worksheet.range(f"B1").value = listALL
    # worksheet.autofit()
    # print()
    # print("Các biến input này nên kiểm tra lại vì nó có vừa 'output' vừa 'input'")
    # for inputcheckaganin in vTest.listInputCheckAgain:
    #     print(inputcheckaganin)
    # print()
    # print("Complete !!!")
####################################################### 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        
        
        
        
        