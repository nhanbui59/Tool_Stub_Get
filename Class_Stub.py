from Gen_Stub import*


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
        match = re.findall("[\w]+\(",all_function)
        list_sub_function = []
        for sub_function in match:
            check = re.search("if\s*\(|while\s*\(|switch\s*\(|sizeof\s*\(",sub_function)
            if check:
                continue
            list_sub_function.append(sub_function.replace("(","").strip())
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
                    init_function += string.strip()
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
    for link in list_all_file:
        test = _Function(link)
        Dic_all_init_source[test.name_file] = test.Get_init_function()
        Dic_function_in_file.update(test.Get_function_file())
    save_file_json(".\\Database\\Database_init_function.json",Dic_all_init_source)
    save_file_json(".\\Database\\Database_function_in_file.json",Dic_function_in_file)
    ######## ___________________________________________________________________________


def main():

    Dic_all_init_source = read_file_json(".\\Database\\Database_init_function.json")
    Dic_function_in_file = read_file_json(".\\Database\\Database_function_in_file.json")
    _function = "Knl_DCDC_Duty"
    print("database file+links code =>",Dic_function_in_file.get(_function))
    if Dic_function_in_file.get(_function) == None:
        return "Not exists function"
    _test = _Function(Dic_function_in_file[_function][1])
    _sub_function = _test.get_sub_function(_test.Get_function(_function))
    for __sub_function in _sub_function:
        # print(Dic_function_in_file[__sub_function][0],__sub_function)
        # print(Dic_all_init_source[Dic_function_in_file[__sub_function][0]][__sub_function][0])
        data = export_stub(Dic_function_in_file[__sub_function][0],Dic_all_init_source[Dic_function_in_file[__sub_function][0]][__sub_function][0])
        print(__sub_function,data[0])

if __name__ == "__main__":
    # test = _Function(r"C:/Projects/Schaeffler_Phase_3/01_Working/01_INPUT/01_Source_Code/V1/TQ250_BL21.00.00(SVA1T21TH_21B08A)/forCUSTOMER/NidecSWC_Lib/nidec_lib/PF/MDL/CDD/CurrentControl/CurrentControl.c")
    # print(test.get_sub_function(test.Get_function("CurrentControl_Pe2Main")))
    # test.Get_init_function()
    # test.Get_function_file()

    main()
    # links = r"C:/Projects/Schaeffler_Phase_3/01_Working/01_INPUT/01_Source_Code/V1/TQ250_BL21.00.00(SVA1T21TH_21B08A)/forNIDEC/0_Src/PF/VSTAR/BSWs/COM/CanNm/ssc/src/CanNm_PBcfg.c"
    # test = _Function(links)
    # print(test.Get_function("IfMdl_GetFlg_Pe2_DebugMode"))
    # test.Get_function_file()


    # export_database_function(r"C:\Projects\Schaeffler_Phase_3\01_Working\01_INPUT\01_Source_Code\V1\TQ250_BL21.00.00(SVA1T21TH_21B08A)")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    pass



























































