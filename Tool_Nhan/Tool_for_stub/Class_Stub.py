from Gen_Stub import*

try:
    g_Dic_all_init_source = read_file_json(".\\Database\\Database_init_function.json")
    g_Dic_function_in_file = read_file_json(".\\Database\\Database_function_in_file.json")
except :
    print("Check not exits database Database_init_function + Database_function_in_file !!!")

class Export_file:
    def __init__(self,links) -> None:
        self.links = links
        self.pattern_file = ".+\.c$|.+\.h$"
        self.pattern_exemple = """
                                  File word : .+\.docx
                                  File excel: .+\.xlsx
                                  File code c: .+\.c$|.+\.h$
                               """
        self.__list_file = []

    @property
    def List_All_file(self):
        self.__list_file = self.export_links(self.links)
        return self.__list_file
    
    @List_All_file.setter
    def List_All_file(self,setter_file):
        self.__list_file = setter_file

    def export_links(self,file_path,list_file = []):
        files = os.listdir(file_path)
        file_path = file_path.replace("\\","/")
        for file in files:
            path_links = os.path.join(file_path, file)
            if os.path.isdir(path_links):
                self.export_links(path_links,list_file)
            else:
                file_tam = re.search("~\$",file)
                if re.search(self.pattern_file,file) != None and file_tam == None:
                    string_links = file_path + "/" + file
                    list_file.append(string_links)
        return list_file

class Read_code:
    def __init__(self,path_file_c):
        self.path_file_C = path_file_c
        self.name_file = path_file_c.replace("/","\\").split("\\")[-1]
        self.name_file_2 = self.name_file.replace(".c","").replace(".h","")
        self.__source_code = self.all_line()

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


class _Function(Read_code):
    def __init__(self, path_file_c):
        super().__init__(path_file_c)
        self.__ctags = "ctags --fields=+ne -o - --sort=no  --c-types=f "
        self.Ctags = self.__ctags + '"' + self.path_file_C + '"'
        self.dic_init_function = {}
        
    def get_line_function(self,command):
        os.popen(command + ' >> Data_ctags.txt').read()
        f = open('Data_ctags.txt', 'r',encoding= "shift-jis",errors="ignore")
        info = f.read()
        f.close()
        os.remove("Data_ctags.txt")
        return info

    def Get_function(self,function):
        data_ctags = self.get_line_function(self.Ctags)
        all_function = data_ctags.replace(self.path_file_C.replace("\\","\\\\"),"")
        all_function = all_function.split("\n")
        source_code = "Not exits function"
        for data in all_function:
            function_name = re.search("[\w]+",data)
            if function_name == None:
                continue
            if function_name.group() == function:
                pattern = "line:(\d+)|end:(\d+)"
                match = re.findall(pattern,data)
                line_start = int(match[0][0],0) - 1
                line_end = int(match[1][1],0)
                source_code = self.source_code.split("\n")
                return "\n".join(source_code[line_start:line_end])

        #### cho các hàm autosar
        if source_code == "Not exits function":
            for data in all_function:
                function_name = re.search(function+"\\s*\\(",data)
                if function_name == None:
                    continue
                pattern = "line:(\d+)|end:(\d+)"
                match = re.findall(pattern,data)
                line_start = int(match[0][0],0) - 1
                line_end = int(match[1][1],0)
                source_code = self.source_code.split("\n")
                return "\n".join(source_code[line_start:line_end])

        return source_code

    def get_sub_function(self,all_function):
        all_function = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",all_function)
        all_function = self.convert_autosar_default(all_function)
        match = re.findall("[\w]+\s*\(",all_function)
        list_sub_function = []
        for sub_function in match:
            check = re.search("if\s*\(|while\s*\(|switch\s*\(|sizeof\s*\(|return\s*\(",sub_function)
            if check:
                continue
            string_sub = sub_function.replace("(","").strip()
            if string_sub not in list_sub_function:
                list_sub_function.append(string_sub)
            # print("Sub Function => ",sub_function.replace("(","").strip())
        try:
            list_sub_function.pop(0)
        except:
            pass
        return list_sub_function

    def Get_init_function(self):
        data_ctags = self.get_line_function(self.Ctags)
        all_function = data_ctags.replace(self.path_file_C.replace("\\","\\\\"),"")
        all_function = all_function.split("\n")
        source_code = self.source_code.split("\n")
        dic_init_function = {}
        for data in all_function:
            function_name = re.search("[\w]+",data)
            if function_name == None:
                continue

            pattern = "line:(\d+)|end:(\d+)"
            match = re.findall(pattern,data)
            line_start = int(match[0][0],0) - 1
            line_end = int(match[1][1],0)
            init_function = ""
            for string in source_code[line_start:line_end]:
                if string.find("{") != -1:
                    init_function += string
                    init_function = re.sub("{[\s\S]*","",init_function).strip()
                    break
                init_function += string.strip()
            ### chuyển hàm autosar về thành hàm như bình thường
            init_function = self.convert_autosar_default(init_function)
            # print(data,"|",init_function)
            try:
                ### bóc tên hàm ra và tạo dic
                function_name = re.search("([\w]+?)\s*\(",init_function)
                if function_name.group(1) not in dic_init_function:
                    dic_init_function[function_name.group(1)] = []
                dic_init_function[function_name.group(1)].append(init_function)
                # print(function_name.group(1),init_function)
            except:
                continue
        self.dic_init_function = dic_init_function
        return dic_init_function

    def Get_function_file(self):
        dic_function_file = {}
        for data in self.Get_init_function():
            dic_function_file[data] = [self.name_file, self.path_file_C]
            # print(data,"==>",dic_function_file[data])

        return dic_function_file

    @staticmethod
    def convert_autosar_default(string_autosar):
        pattern_autosar = "FUNC\s*\(.+?\)|P2FUNC\s*\(.+?\)|FUNC_P2VAR\s*\(.+?\)|FUNC_P2CONST\s*\(.+?\)|CONSTP2VAR\s*\(.+?\)|CONSTP2CONST\s*\(.+?\)|P2VAR\s*\(.+?\)|P2CONST\s*\(.+?\)|VAR\s*\(.+?\)|CONST\s*\(.+?\)"
        match = re.findall(pattern_autosar,string_autosar)
        for autosar in match:
            try:
                typedef_match = re.search("\((.+)\)",autosar).group(1).split(",")[0].strip()
            except:
                continue
            string_autosar = string_autosar.replace(autosar,typedef_match)
        return string_autosar



def export_database_function(path_source_code):
    ######## xuất database function
    Dic_all_init_source = {}
    Dic_function_in_file = {}
    # All_file_code = Export_file(r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)\forCUSTOMER")
    All_file_code = Export_file(path_source_code)
    list_all_file = All_file_code.List_All_file

    max_file = len(list_all_file)
    progessbar = 1
    progessbar__ = 1
    progessbar_old = 1

    for link in list_all_file:
        try:
            test = _Function(link)
            Dic_function_in_file.update(test.Get_function_file())
            Dic_all_init_source[test.name_file] = test.dic_init_function
        except:
            print(link, "Export Error!")

        progessbar__ = int((progessbar/max_file)*100)
        if progessbar__ != progessbar_old:
            print(progessbar__)
            progessbar_old = progessbar__
        progessbar += 1

    save_file_json(".\\Database\\Database_init_function.json",Dic_all_init_source)
    save_file_json(".\\Database\\Database_function_in_file.json",Dic_function_in_file)
    ######## ___________________________________________________________________________


def callDatebase():
    global g_Dic_all_init_source
    global g_Dic_function_in_file
    try:
        g_Dic_all_init_source = read_file_json(".\\Database\\Database_init_function.json")
        g_Dic_function_in_file = read_file_json(".\\Database\\Database_function_in_file.json")
    except :
        print("Check not exits database Database_init_function + Database_function_in_file !!!")


def main():
    Dic_all_init_source = read_file_json(".\\Database\\Database_init_function.json")
    Dic_function_in_file = read_file_json(".\\Database\\Database_function_in_file.json")
    _function = "DcdcCtrl_Ontime_SwLimit_Async"
    print("database file+links code =>",Dic_function_in_file.get(_function))
    if Dic_function_in_file.get(_function) == None:
        return "Not exists function"
    _test = _Function(Dic_function_in_file[_function][1])
    _sub_function = _test.get_sub_function(_test.Get_function(_function))
    for __sub_function in _sub_function:
        # print(Dic_function_in_file[__sub_function][0],__sub_function)
        # print(Dic_all_init_source[Dic_function_in_file[__sub_function][0]][__sub_function][0])
        data = export_stub(Dic_function_in_file[__sub_function][0],Dic_all_init_source[Dic_function_in_file[__sub_function][0]][__sub_function][0])
        print(data[1].strip())
    # return data[0]

def export_stub_for_function(function = ""):

    Dic_all_init_source = read_file_json(".\\Database\\Database_init_function.json")
    Dic_function_in_file = read_file_json(".\\Database\\Database_function_in_file.json")
    _function = function
    # print("database file+links code =>",Dic_function_in_file.get(_function))
    if Dic_function_in_file.get(_function) == None:
        return ["Not exists function", "",""]
    _test = _Function(Dic_function_in_file[_function][1])
    _sub_function = _test.get_sub_function(_test.Get_function(_function))

    list_stub_file_c = []
    list_stub_file_h = []
    list_stub_list_function_call = []
    list_function_not_exits = []
    stub_file_c = ""
    stub_file_h = ""
    stub_list_function_call = ""
    for __sub_function in _sub_function:
        try:
            data_stub = export_stub(Dic_function_in_file[__sub_function][0],Dic_all_init_source[Dic_function_in_file[__sub_function][0]][__sub_function][0])
            list_stub_file_c.append(data_stub[0])
            list_stub_file_h.append(data_stub[1].strip())
            list_stub_list_function_call.append(data_stub[2])
        except:
            print("Function sub not exits in database_functions ==>> " + __sub_function)
            list_function_not_exits.append(__sub_function)
    
    stub_file_c = "\n\n".join(list_stub_file_c)
    stub_file_h = "\n\n".join([s for s in list_stub_file_h if s!=""])
    stub_list_function_call = "".join(list_stub_list_function_call)
    return [stub_file_c, stub_file_h, stub_list_function_call, list_function_not_exits]


def export_stub_for_sheet_IO(function = ""):

    Dic_all_init_source = read_file_json(".\\Database\\Database_init_function.json")
    Dic_function_in_file = read_file_json(".\\Database\\Database_function_in_file.json")
    _function = function

    # print("database file+links code =>",Dic_function_in_file.get(_function))
    if Dic_function_in_file.get(_function) == None:
        return "Not exists function"

    _test = _Function(Dic_function_in_file[_function][1])
    _sub_function = _test.get_sub_function(_test.Get_function(_function))

    list_string_sheet_IO = []
    for __sub_function in _sub_function:
        string_stub_IO = "AMSTB_"+__sub_function
        try:
            data_stub = export_stub(Dic_function_in_file[__sub_function][0],Dic_all_init_source[Dic_function_in_file[__sub_function][0]][__sub_function][0])
            pattern_IO = "static.+(AMOUT_.+)\[|static.+(AMIN_.+)\[|static.+(AMSTB_Ver)\s*\[|static.+(AMOUT_cnt)\s*;"
            list_match_IO = re.findall(pattern_IO,data_stub[0])
            pattern_all_IO = "static.+AMOUT_.+\[|static.+AMIN_.+\[|static.+AMSTB_Ver\s*\[|static.+AMOUT_cnt\s*;"
            list_match_all_IO = re.findall(pattern_all_IO,data_stub[0])
            for data_IO, data_all_IO in zip(list_match_IO, list_match_all_IO):
                # print("AMSTB_"+__sub_function,data_IO)
                # print(data_IO, data_all_IO)
                for _data_IO in data_IO:
                    _data_IO = _data_IO.strip()
                    if _data_IO == "AMOUT_cnt":
                        list_string_sheet_IO.append(string_stub_IO + "@" + _data_IO)
                    elif _data_IO != "":
                        if data_all_IO.find("*") != -1 and data_all_IO.find("AMIN_") != -1:
                            list_string_sheet_IO.append("$" + string_stub_IO + "@" + _data_IO + "[0]")
                            list_string_sheet_IO.append(string_stub_IO + "@" + _data_IO + "[0][0]")
                        else:
                            list_string_sheet_IO.append(string_stub_IO + "@" + _data_IO + "[0]")
            list_string_sheet_IO.append("\n")
        except:
            print("Function sub not exits in database_functions ==>> " + __sub_function)

    return list_string_sheet_IO


def export_stub_for_function_check_optimize(function = "",string_optimize = "",string_code_stub="",list_stub_file_c = [], list_stub_file_h = [], list_stub_list_function_call = []):

    #### tên hàm cần gen stub
    _function = function

    if g_Dic_function_in_file.get(_function) == None:
        print("Not exists function ==>>" + _function)
        return ["Not exists function", "",""]

    _test = _Function(g_Dic_function_in_file[_function][1])
    _sub_function = _test.get_sub_function(_test.Get_function(_function))

    stub_file_c = ""
    stub_file_h = ""
    stub_list_function_call = ""

    ### pattern check optimaze_code
    pattern_check_optimize = "\s*0x[\w]{8}\s+0x[\w]{8}\s+\d+\s+[A-Za-z]+\s+"

    for __sub_function in _sub_function:

        if string_code_stub.find("AMSTB_"+__sub_function) != -1:
            continue

        if re.search(pattern_check_optimize + __sub_function,string_optimize) != None: # or string_optimize.find(__sub_function) == -1:
            try:
                data_stub = export_stub(g_Dic_function_in_file[__sub_function][0],g_Dic_all_init_source[g_Dic_function_in_file[__sub_function][0]][__sub_function][0])
                list_stub_file_c.append(data_stub[0])
                list_stub_file_h.append(data_stub[1].strip())
                list_stub_list_function_call.append(data_stub[2])
            except:
                print("Function sub not exits in database_functions ==>> " + __sub_function)
        else:
            export_stub_for_function_check_optimize(__sub_function,string_optimize,string_code_stub,list_stub_file_c,list_stub_file_h,list_stub_list_function_call)
    
    stub_file_c = "\n\n".join(list_stub_file_c)
    stub_file_h = "\n\n".join([s for s in list_stub_file_h if s!=""])
    stub_list_function_call = "".join(list_stub_list_function_call)
    return [stub_file_c, stub_file_h, stub_list_function_call]


def export_stub_for_IO_check_optimize(function = "",string_optimize = "",list_string_sheet_IO = []):

    #### tên hàm cần gen stub
    _function = function

    if g_Dic_function_in_file.get(_function) == None:
        print("Not exists function ==>>" + _function)
        return "Not exists function"

    _test = _Function(g_Dic_function_in_file[_function][1])
    _sub_function = _test.get_sub_function(_test.Get_function(_function))

    ### pattern check optimaze_code
    pattern_check_optimize = "\s*0x[\w]{8}\s+0x[\w]{8}\s+\d+\s+[A-Za-z]+\s+"

    for __sub_function in _sub_function:
        string_stub_IO = "AMSTB_"+__sub_function

        if re.search(pattern_check_optimize + __sub_function,string_optimize) != None:# or string_optimize.find(__sub_function) == -1:
            try:
                data_stub = export_stub(g_Dic_function_in_file[__sub_function][0],g_Dic_all_init_source[g_Dic_function_in_file[__sub_function][0]][__sub_function][0])
                pattern_IO = "static.+(AMOUT_.+)\[|static.+(AMIN_.+)\[|static.+(AMSTB_Ver)\s*\[|static.+(AMOUT_cnt)\s*;"
                list_match_IO = re.findall(pattern_IO,data_stub[0])
                pattern_all_IO = "static.+AMOUT_.+\[|static.+AMIN_.+\[|static.+AMSTB_Ver\s*\[|static.+AMOUT_cnt\s*;"
                list_match_all_IO = re.findall(pattern_all_IO,data_stub[0])
                for data_IO, data_all_IO in zip(list_match_IO, list_match_all_IO):
                    # print("AMSTB_"+__sub_function,data_IO)
                    # print(data_IO, data_all_IO)
                    for _data_IO in data_IO:
                        _data_IO = _data_IO.strip()
                        if _data_IO == "AMOUT_cnt":
                            list_string_sheet_IO.append(string_stub_IO + "@" + _data_IO)
                        elif _data_IO != "":
                            if data_all_IO.find("*") != -1 and data_all_IO.find("AMIN_") != -1:
                                list_string_sheet_IO.append("$" + string_stub_IO + "@" + _data_IO + "[0]")
                                list_string_sheet_IO.append(string_stub_IO + "@" + _data_IO + "[0][0]")
                            else:
                                list_string_sheet_IO.append(string_stub_IO + "@" + _data_IO + "[0]")
                list_string_sheet_IO.append("\n")
            except:
                print("Function sub not exits in database_functions ==>> " + __sub_function)
        else:
            index_list_1 = len(list_string_sheet_IO)
            export_stub_for_IO_check_optimize(__sub_function,string_optimize,list_string_sheet_IO)
            index_list_2 = len(list_string_sheet_IO)
            if index_list_1 == index_list_2:
                if g_Dic_function_in_file.get(_function) == None:
                    print("Not exists function ==>>" + _function)
                else:
                    function_return = _Function(g_Dic_function_in_file[__sub_function][1])
                    variable_returne = function_return.Get_function(__sub_function)
                    variable_returne = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",variable_returne)
                    match_return = re.search("return([\[\]\s\(\)\w\*\.\-\>]+);",variable_returne)
                    checkLineStament = re.findall(".+;",variable_returne) # kiếm tra có bao nhiêu câu lệnh, đa số setter và getter đều chỉ có 1 dòng lệnh
                    if len(checkLineStament) == 1:
                        if match_return != None:
                            list_string_sheet_IO.append(match_return.group(1).replace("(","").replace(")","").strip())
                            list_string_sheet_IO.append("\n")
                        else:
                            match_return = re.search("([\w]+)\s*=",variable_returne)
                            if match_return != None:
                                list_variable = re.findall("([\w]+)\s*=",variable_returne)
                                string_match = list_variable[-1].replace("=","").strip()
                                list_string_sheet_IO.append(string_match)
                                list_string_sheet_IO.append("\n")

    return list_string_sheet_IO


def export_stub_for_function_check_optimize_not_stub(function = "",string_optimize = "",string_code_stub="",list_stub_file_c = [], list_stub_file_h = [], list_stub_list_function_call = []):

    #### tên hàm cần gen stub
    _function = function

    if g_Dic_function_in_file.get(_function) == None:
        print("Not exists function ==>>" + _function)
        return ["Not exists function", "",""]

    _test = _Function(g_Dic_function_in_file[_function][1])
    _sub_function = _test.get_sub_function(_test.Get_function(_function))

    stub_file_c = ""
    stub_file_h = ""
    stub_list_function_call = ""

    ### pattern check optimaze_code
    pattern_check_optimize = "\s*0x[\w]{8}\s+0x[\w]{8}\s+\d+\s+[A-Za-z]+\s+"

    for __sub_function in _sub_function:
        if re.search(pattern_check_optimize + __sub_function,string_optimize) != None:# or string_optimize.find(__sub_function) == -1:
            try:
                data_stub = export_stub(g_Dic_function_in_file[__sub_function][0],g_Dic_all_init_source[g_Dic_function_in_file[__sub_function][0]][__sub_function][0])
                list_stub_file_c.append(data_stub[0])
                list_stub_file_h.append(data_stub[1].strip())
                list_stub_list_function_call.append(data_stub[2])
            except:
                print("Function sub not exits in database_functions ==>> " + __sub_function)
        else:
            export_stub_for_function_check_optimize_not_stub(__sub_function,string_optimize,string_code_stub,list_stub_file_c,list_stub_file_h,list_stub_list_function_call)
    
    stub_file_c = "\n\n".join(list_stub_file_c)
    stub_file_h = "\n\n".join([s for s in list_stub_file_h if s!=""])
    stub_list_function_call = "".join(list_stub_list_function_call)
    return [stub_file_c, stub_file_h, stub_list_function_call]




if __name__ == "__main__":
    # test = _Function(r"C:/Projects/Schaeffler_Phase_3/01_Working/01_INPUT/01_Source_Code/V1/TQ250_BL21.00.00(SVA1T21TH_21B08A)/forCUSTOMER/NidecSWC_Lib/nidec_lib/PF/MDL/CDD/CurrentControl/CurrentControl.c")
    # print(test.get_sub_function(test.Get_function("CurrentControl_Pe2Main")))
    # test.Get_init_function()
    # test.Get_function_file()

    
    # links = r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)\forCUSTOMER\NidecSWC_Lib\nidec_lib\PF\MDL\DcDcCtrl\DcDcCtrl.c"
    # test = _Function(links)
    # print(test.Get_init_function())
    # print(test.Get_function_file())


    # export_database_function(r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)")
    
    # export_stub_for_sheet_IO("DcdcCtrl_Ontime_Main_25us")
    
    string = "DcdcCtrl_Mng_Main_25us|BL21.04.00_Pre(7be717f0075)_NORMAL_TO_INLINE".split("|")
    path_check_optimize = r"C:\\Projects\\Schaeffler_Phase_4\\01_Working\\01_INPUT\\01_Source_Code\\V1\\06_Map_files"
    
    path_check_optimize = path_check_optimize + "\\" +  string[1].strip() + "\\Nidec_Lib_link_test.map"
    function = string[0].strip()

    check_optimize = Read_code(path_check_optimize)
    string_check_optimize = check_optimize.source_code
    
    # pattern_check_optimize = "\s*0x[\w]{8}\s+0x[\w]{8}\s+\d+\s+[A-Za-z]+\s+" + function
    # print(re.search(pattern_check_optimize, string_check_optimize))
    
    ####kiểm tra optimaze và trong stub đã có chưa
    # data_stub = export_stub_for_function_check_optimize(function,string_check_optimize)
    # print(data_stub[0])
    
    data_stub = export_stub_for_IO_check_optimize(function,string_check_optimize)
    
    for _i in data_stub:
        print(_i)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    pass



























































