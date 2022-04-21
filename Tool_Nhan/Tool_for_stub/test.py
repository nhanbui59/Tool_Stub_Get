

from re import S


def reves(string=[],end=0):
    if len(string)/2 <= end:
        return 0
    string[0+end],string[len(string)-1-end] = string[len(string)-1-end],string[0+end]
    reves(string,end+1)
    return string

# string = "xin chào bạn"
# string = "".join(reves(list(string)))
# print(string)

def quicksort(_list):
    if len(_list) < 2:
        return _list
    else:
        k = _list[0]
        L = [i for i in _list[1:] if i <= k]
        R = [i for i in _list[1:] if i > k]
        return quicksort(L) + [k] + quicksort(R)

# m = [99,100,40,50,3,2,5,6,9]
# print(quicksort(m))

import xlwings

source_code_input_file = r"C:\Projects\Schaeffler_Phase_4\01_Working\01_INPUT\09_Exported_data_from_source_codes\TQ250_BL21.04.00(SVA1T21TH_22311A)\Macro.csv"
wbk = xlwings.Book(source_code_input_file)

print(wbk.sheets[0].range("F3").options(numbers=lambda x: str(int(x))).value)
wbk.app.quit()




























