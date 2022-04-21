import re
import os
import json




def datatype(conv):
    type = "VOID"
    if conv == "ULONG" or conv == "HULONG" :
        type = "unsigned long"
    elif conv == "USHORT" or conv == "HUSHORT" :
        type = "unsigned short"
    elif conv == "UCHAR" or conv == "HUCHAR" :
        type = "unsigned char"
    elif conv == "LONG" or conv == "HLONG" :
        type = "signed long"
    elif conv == "SHORT" or conv == "HSHORT" :
        type = "signed short"
    elif conv == "CHAR" or conv == "HCHAR" :
        type = "signed char"
    elif conv == "FLAG" or conv == "HFLAG" :
        type = "unsigned char"
    elif conv == "BOOL" :
        type = "unsigned char"
    elif conv == "FLOAT" :
        type = "float"
    elif conv == "CULONG" or conv == "HCULONG" :
        type = "volatile const unsigned long"
    elif conv == "CUSHORT" or conv == "HCUSHORT" :
        type = "volatile const unsigned short"
    elif conv == "CUCHAR" or conv == "HCUCHAR" :
        type = "volatile const unsigned char"
    elif conv == "CLONG" or conv == "HCLONG" :
        type = "volatile const signed long"
    elif conv == "CSHORT" or conv == "HCSHORT" :
        type = "volatile const signed short"
    elif conv == "CCHAR" or conv == "HCCHAR" :
        type = "volatile const signed char"
    elif conv == "CFLAG" or conv == "HCFLAG" :
        type = "volatile const unsigned char"
    elif conv == "CFLOAT" :
        type = "volatile const float"
    elif conv == "VOID" :
        type = "void"
    else:
        type = conv
    return type

def export_stub(file, string_all_function):
    file_name = file
    string = string_all_function
    string = re.sub("\/\*[\s\S]*?\*\/|\/\/.*","",string)
    string = string.replace("static","").replace("inline", "").strip() #xóa chữ static và inline trong hàm

    ## tách kiểu dữ liệu của function
    pattern_typedef_function = "[^\s]+\s*\(.+\)"
    typedef_function = re.sub(pattern_typedef_function,"",string).strip()


    ## tách tên function và các argument
    pattern_name_and_argument = "([\S]+)\s*\((.*)\)"
    name_and_argument = re.findall(pattern_name_and_argument,string)
    name_function = name_and_argument[0][0].strip() ### tách tên
    argument_function = name_and_argument[0][1] ### tách argument


    ## chuỗi stub chính
    Stringstub = []
    Stringstub_h = []
    Stringstub.append("/* WINAMS_STUB[" + file_name + ":" + name_function + ":AMSTB_" + name_function + ":inout::array<outside>:counter<AMOUT_cnt>] */\n")
    Stringstub.append("/*\t" + name_function + " => Stub\t*/\n")

    ##khai báo hàm trong stub AMSTB_ + tên hàm + ( 
    typedef_function = datatype(typedef_function)
    Stringstub.append(typedef_function + " " + "AMSTB_" + name_function + "(")


    string_AMin = []
    string_AMOUT = []
    string_AMSTB_Ver = "\n\t" + "if(AMSTB_Ver[AMOUT_cnt] == 1)" + "\n\t{"
    string_call_stub = ""

    ## funtion dành cho không có argument ::
    check_null_or_void = argument_function.strip()
    if check_null_or_void == "" or check_null_or_void == "void" or check_null_or_void == "VOID":
        if typedef_function != "void" :
            Stringstub.append(")\n{")
            Stringstub.append("\n\tstatic " + typedef_function + " volatile AMIN_return[AMCALLMAX_" + name_function + "];")
            Stringstub.append("\n\tstatic unsigned long volatile AMOUT_cnt;")
            Stringstub.append("\n\tAMOUT_cnt++;")
            Stringstub.append("\n\n\treturn AMIN_return[AMOUT_cnt - 1];\n}")
            Stringstub_h.append("\n/*WINAMS_STUB_ARRAY_SIZE[AMSTB_" + name_function + "]*/")
            Stringstub_h.append("\n#define AMCALLMAX_" + name_function + " 1\n")
        else:
            Stringstub.append(")\n{\n	static unsigned long volatile AMOUT_cnt;\n	AMOUT_cnt++;\n}")
        string_call_stub = "AMSTB_" + name_function + "();\n"
    else:
        check_pointer = False
        list_argument = check_null_or_void.split(",")
        for argument in list_argument:
            string_process = argument.replace("const","").replace("volatile","").strip()
            if string_process.find("*") != -1:
                check_pointer = True
                patten = "(.*)\s*\*\s*(.*)"
                stringline = re.findall(patten,string_process)
                stringline[0] = list(stringline[0])
                stringline[0][0] = datatype(stringline[0][0].strip())
                stringline[0][1] = stringline[0][1].strip()
                string_AMin.append("\n\tstatic " + stringline[0][0] + " *volatile  AMOUT_" + stringline[0][1] + "[AMCALLMAX_" + name_function + "];")
                string_AMin.append("\n\tstatic " + stringline[0][0] + " volatile  AMIN_" + stringline[0][1] + "[AMCALLMAX_" + name_function + "];")
                string_AMOUT.append("\n\tAMOUT_" + stringline[0][1] + "[AMOUT_cnt] = " + stringline[0][1] + ";")
                if argument == list_argument[-1]:
                    Stringstub[-1] += stringline[0][0] + " *" + stringline[0][1] +")\n{\n"
                else:
                    Stringstub[-1] += stringline[0][0] + " *" + stringline[0][1] +", "
                string_AMSTB_Ver += "\n\t\t*" + stringline[0][1] + " = " + "AMIN_" + stringline[0][1] + "[AMOUT_cnt];"
            else:
                patten = "([_a-zA-Z0-9]+)\s+(.*)"
                stringline = re.findall(patten,string_process)
                stringline[0] = list(stringline[0])
                stringline[0][0] = datatype(stringline[0][0].strip())
                stringline[0][1] = stringline[0][1].strip()
                string_AMin.append("\n\tstatic " + stringline[0][0] + " volatile AMOUT_" + stringline[0][1] + "[AMCALLMAX_" + name_function + "];")
                string_AMOUT.append("\n\tAMOUT_" + stringline[0][1] + "[AMOUT_cnt]" + " = " + stringline[0][1] +";")
                if argument == list_argument[-1]:
                    Stringstub[-1] += stringline[0][0] + " " + stringline[0][1] + ")\n{\n"
                else:
                    Stringstub[-1] += stringline[0][0] + " " + stringline[0][1] +", "

        string_AMSTB_Ver += "\n\t}\n\telse\n\t{\n\t\t /* add */\n\t}"
        
        if typedef_function != "void" :
            string_AMin.insert(0,"\n\tstatic " + typedef_function + " volatile AMIN_return[AMCALLMAX_" + name_function + "];")

        for init_amin in string_AMin:
            Stringstub.append(init_amin)

        if check_pointer:
            Stringstub.append("\n\tstatic unsigned char volatile  AMSTB_Ver[AMCALLMAX_" + name_function + "];")

        Stringstub.append("\n\tstatic unsigned long volatile AMOUT_cnt;\n")

        for _amout in string_AMOUT:
            Stringstub.append(_amout)

        if check_pointer:
            Stringstub.append("\n" + string_AMSTB_Ver)

        Stringstub.append("\n\tAMOUT_cnt++;")

        if typedef_function != "void" :
            Stringstub.append("\n\n\treturn AMIN_return[AMOUT_cnt - 1];")

        Stringstub.append("\n}")
        Stringstub_h.append("\n/*WINAMS_STUB_ARRAY_SIZE[AMSTB_" + name_function + "]*/")
        Stringstub_h.append("\n#define AMCALLMAX_" + name_function + " 1\n")


        string_call_stub = "AMSTB_" + name_function + "("
        list_argument_call = ["0" for i in range(len(list_argument))]
        string_call_stub = string_call_stub + ", ".join(list_argument_call) + ");\n"

    return ["".join(Stringstub), "".join(Stringstub_h), string_call_stub, string_AMin]

def save_file_json(path_save,dic_data):
    # Write JSON file
    with open(path_save, 'w', encoding='utf-8', errors="ignore") as outfile:
        json.dump(dic_data,outfile,indent=4, ensure_ascii=False)
        outfile.close()
    return path_save

def read_file_json(path_json):
    # Write JSON file
    with open(path_json, 'r', encoding='utf-8', errors="ignore") as outfile:
        json_data = json.load(outfile)
        outfile.close()
    return json_data

if __name__ == "__main__":
    data = export_stub("DcDcCtrl_ontime.c", "ULONG   IfCfc_Shift_LR ( ULONG indat, ULONG shift_size )")
    print(data[0])












