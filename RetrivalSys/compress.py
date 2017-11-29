
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
            num_len += now_len
            num = now_num
            get_len = True
        else:
            # 解剩余的偏移码我偷懒直接移位求和了，实际还需要改进，按解得的长度去解码
            num = (num << 8) + code[i]
    num += 1 << num_len
    return num


bt = Gamma_encode(1025)
print(bt)
num = Gamma_decode(bt)
print(num)
