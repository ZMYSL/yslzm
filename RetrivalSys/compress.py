import struct

# Gamma编码
def Gamma_encode(num):
    if not isinstance(num, int):
        raise TypeError("num type must be int")
    if num == 0:
        raise ValueError("Gamma encode num = 0")
    #把原字符转换为二进制编码，去掉第一个bit
    ob_code = bin(num)[2:]
    l_code = ''
    b_code = ''
    #一元码l_code
    for i in range(len(ob_code) - 1):
        l_code += '1'
    l_code += '0'
    if len(ob_code) > 1:
        b_code = ob_code[1:]
    #最终的gamma编码
    code_ult = l_code + b_code
    return code_ult
'''
def Gamma_decode(code):
    if not isinstance(code, bytes):
        raise TypeError("code type must be bytes")
    num_len = 0
    for i in range(len(code)):
        if code[i] == '1':
            num_len += 1
        else:
            break
    num = 2 ** num_len + int(code[num_len + 1:], 2)
    return num
'''
#将一个二进制串解码，解码结果以list形式返回
def Gamma_decode(code):
    if not isinstance(code, str):
        raise TypeError("code type must be bytes")
    num = []
    flag = 0
    code_length = len(code)
    while flag < code_length:
        num_len = 0
        for i in range(flag, code_length):
            if code[i] == '1':
                num_len += 1
            else:
                break
        start = flag + num_len + 1
        end = flag + 2 * num_len + 1
        if(start == end):
            tmp_num = 0
        else:
            tmp_num = 2 ** num_len + int(code[start:end], 2)
        #print(start)
        num.append(tmp_num)
        flag = end
    return num

#print(Gamma_decode('1100011100001010'))


