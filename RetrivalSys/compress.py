# -*- coding: utf-8 -*-
import json
import struct
import binascii
# Gamma编码
def Gamma_encode(num):
    """Gamma编码:
            Args:
                num: int型数字.
            Output:
                num_list: bytes型数组，不定长，末尾字节是从高位开始编码，低位可能没有使用.
            """
    if not isinstance(num, int):
        raise TypeError("num type must be int")
    if num == 0:
        raise ValueError("Gamma encode num = 0")
    ob_code = bin(num)[2:]
    l_code = ''
    b_code = ''
    for i in range(len(ob_code) - 1):
        l_code += '1'
    l_code += '0'
    if len(ob_code) > 1:
        b_code = ob_code[1:]
    # 先得到字符串编码，01二进制但是是str类型
    code_ult = l_code + b_code
    num_list = []
    bit8 = 0
    # 从高位开始8位存成一个整数，然后用bytes重构
    while bit8 < len(code_ult):
        now = bit8
        end = bit8 + 8 if bit8 + 8 <= len(code_ult) else len(code_ult)
        num_list.append(int(code_ult[now:end], 2))
        bit8 += 8

    return bytes(num_list)

# Gamma编码,对一个list进行编码
def Gamma_encode_all(numlist):
    """Gamma编码:
                Args:
                    numlist: int型list.
                Output:
                    code_list: bytes型数组，不定长，末尾字节是从高位开始编码，低位可能没有使用.
                    bias_list: int型数组，保留每个IDF，即倒排起始位偏移量
                """
    if not isinstance(numlist, list):
        raise TypeError("numlist type must be list")
    code_list = []
    code_ult = ''
    bias_list = []
    bias = 0
    get_df = False
    for i in range(len(numlist)):
        # if not isinstance(numlist[i], list):
        #     raise TypeError("numlist element type must be int")
        if numlist[i] == 0:
            raise ValueError("Gamma encode num = 0")
        if not get_df:
            get_df = True
            bias_list.append(bias)
            df = numlist[i] * 2
            doc_sum = 0
        else:
            doc_sum += 1
            if doc_sum >= df:
                get_df = False
        ob_code = bin(numlist[i])[2:]
        l_code = ''
        b_code = ''
        for i in range(len(ob_code) - 1):
            l_code += '1'
        l_code += '0'
        if len(ob_code) > 1:
            b_code = ob_code[1:]
        # 先得到字符串编码，01二进制但是是str类型
        now_code = l_code + b_code
        code_ult += now_code
        bias += len(now_code)

    bit8 = 0
    # 从高位开始8位存成一个整数，然后用bytes重构
    while bit8 < len(code_ult):
        now = bit8
        end = bit8 + 8 if bit8 + 8 <= len(code_ult) else len(code_ult)
        code_list.append(int(code_ult[now:end], 2) << (8 - (end - now)))
        bit8 += 8
    print(code_ult)
    return bytes(code_list), bias_list

# Gamma解码
def Gamma_decode(code):
    """Gamma编码:
                Args:
                    code: bytes型数组，.
                Output:
                    num: 解码后的数字.
                TODO: 现在只能解标准的一个正确编码，
                """
    if not isinstance(code, bytes):
        raise TypeError("code type must be bytes")
    num = 0
    num_len = 0
    code_len = 0
    get_len = False
    for i in range(len(code)):
        # 先解长度码
        if code[i] == 255 and not get_len:
            num_len += 8
        elif not get_len:
            now_num = code[i]
            now_len = 0
            # 从高位找1
            for j in range(8):
                if (1 << (7 - j)) <= now_num:
                    now_num -= (1 << (7 - j))
                    now_len += 1
                else:
                    break
            code_len += 16-now_len-1
            num_len += now_len
            num = now_num
            get_len = True
        else:
            # 解剩余的偏移码我偷懒直接移位求和了，实际还需要改进，按解得的长度去解码
            if code_len<num_len:
                num = (num << 8)+code[i]
                code_len += 8
            else:
                left_len=num_len+8-code_len
                num = (num << left_len) + (code[i] >> 8 - left_len)

    num += 1 << num_len
    return num

# Gamma解码
def Gamma_decode_all(code, bias):
    """Gamma解码:从指定偏移位置解出对应的倒排记录
                Args:
                    code: bytes型数组.
                    bias: int型变量
                Output:
                    numlist: 解码后的倒排表.
                """
    if not isinstance(code, bytes):
        raise TypeError("code type must be bytes")
    if not isinstance(bias, int):
        raise TypeError("bias type must be bytes")
    num_len = 0
    code_len = 0
    get_len = False

    bytes_id = bias // 8
    bias_id = bias % 8

    get_df = False
    df = 0
    for i in range(bytes_id, len(code)):
        # 先解长度码
        if i == bytes_id:
            now_num = code[i] & (1 << (8 - bias_id) - 1)
        if code[i] == 255 and not get_len:
            num_len += 8
        elif not get_len:
            if i > bytes_id:
                now_num = code[i]
            now_len = 0
            # 从高位找1
            for j in range(8):
                if (1 << (7 - j)) <= now_num:
                    now_num -= (1 << (7 - j))
                    now_len += 1
                else:
                    get_len = True
                    len_end = j + 1
                    num = 0
                    break
            if get_len:
                l = 0
                for j in range(len_end, 8):
                    if l < now_len:
                        num += (now_num & (1 << 7 - j))
                        l += 1


            # code_len += 16-now_len-1
            # num_len += now_len
            # num = now_num
        else:
            # 解剩余的偏移码我偷懒直接移位求和了，实际还需要改进，按解得的长度去解码
            if code_len<num_len:
                num = (num << 8)+code[i]
                code_len += 8
            else:
                left_len = num_len + 8 - code_len
                num = (num << left_len) + (code[i] >> 8 - left_len)

    num += 1 << num_len
    return num

'''
bt = Gamma_encode(1025)
print(bt)
print(type(bt))
num = Gamma_decode(b'\xff\xc0\x0f')
print(num)
'''
def index_encode():
    first_index = 0
    bia = 0
    k=0
    index_file = open("components/Drama/Index_SPIMI.txt", 'r', encoding='utf-8')
    #index_file = open("components/index.txt", 'r', encoding='utf-8')
    encode_index_file = open("components/encode_index.txt", 'wb')
    dict_file = open("components/dict.txt", 'w', encoding='utf-8')
    line = index_file.readline()#调用文件的 readline()方法
    while line:
        word_index_dict=json.loads(line)
        index_list=list(word_index_dict.values())[0]
        first_index=first_index+bia
        term_dict = {list(word_index_dict.keys())[0]: first_index}
        term_str = json.dumps(term_dict)
        dict_file.write(term_str + '\n')
        code=Gamma_encode(index_list[0])
        bia+=len(code)
        encode_index_file.write(code)
        for i in range(1,len(index_list)):
            code1 = Gamma_encode(index_list[i][0])
            code2 = Gamma_encode(index_list[i][1])
            bia += len(code1)
            bia += len(code2)
            encode_index_file.write(code1)
            encode_index_file.write(code2)
        line = index_file.readline()

    index_file.close()
    encode_index_file.close()

def index_decode(num):
    encode_index_file = open("components/Drama/encode_index.txt", 'rb')
    code=encode_index_file.read()
    print(code[num])



# index_encode()
#index_decode(58)

numlist = [2, 2, 2, 2, 2, 1, 2, 2]
code, bias = Gamma_encode_all(numlist)
print(code)
print(bias)

# Gamma_decode_all(code, 15)