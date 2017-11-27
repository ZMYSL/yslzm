
# Gamma编码
def Gamma_encode(num):
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
    code_ult = l_code + b_code
    return code_ult

# Gamma解码
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

