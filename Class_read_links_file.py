import os
import re



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