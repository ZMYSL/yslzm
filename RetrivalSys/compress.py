# -*- coding: utf-8 -*-
import json

# Gamma编码,对一个list进行编码
def Gamma_encode_all(numlist, encode_file, last_code, last_bias, lastblock=False):
    """Gamma编码:
                Args:
                    encode_file: 需要写入编码的文件
                    last_code: 上次按8位编码剩余的编码
                    last_bias: 上次按8位编码剩余的位数
                    numlist: int型list.
                Output:
                    bias_list: int型数组，保留每个DF，即倒排起始位偏移量
                """
    if not isinstance(numlist, list):
        raise TypeError("numlist type must be list")
    code_list = []
    code_ult = last_code
    bias_list = []
    bias = last_bias
    get_df = False
    listsum = len(numlist)
    for i in range(listsum):
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
    unbyte_code = ''
    # 从高位开始8位存成一个整数，然后用bytes重构
    while bit8 < len(code_ult):
        now = bit8
        end = bit8 + 8
        if end > len(code_ult):
            if lastblock:
                end = len(code_ult)
            else:
                unbyte_code = code_ult[now:]
                break
        code_list.append(int(code_ult[now:end], 2) << (8 - (end - now)))
        bit8 += 8
    encode_file.write(bytes(code_list))
    return bias_list, unbyte_code, bias

# Gamma解码,直接从文件中在偏移位置进行解码
def Gamma_decode_all(args, bias):
    """Gamma解码:从指定偏移位置解出对应的倒排记录
                Args:
                    bias: int型变量
                Output:
                    index: 解码后的倒排表,和SPIMI生成的格式一致.
                """
    if not isinstance(bias, int):
        raise TypeError("bias type must be bytes")
    bytes_id = bias // 8
    bias_id = bias % 8
    encode_path = args.cpn_dir + 'encode_index.txt'
    encode_index_file = open(encode_path, 'rb')
    block = 1024 * 8192
    block_sum = bytes_id // block
    bytes_rest = bytes_id % block
    for i in range(block_sum):
        encode_index_file.read(block)
    encode_index_file.read(bytes_rest)


    def decode_pos(lastbyte, bitid):
        get_len = False
        num_len = 0
        l = 0
        num = 0
        # for i in range(byteid, len(code)):
        byte_id = 0
        read = False
        if lastbyte == None:
            read = True
        while True:
            if read:
                code = encode_index_file.read(1)[0]
            else:
                code = lastbyte
                read = True
            if byte_id == 0:
                now_num = code & ((1 << (8 - bitid)) - 1)
            else:
                now_num = code
            if not get_len and now_num == 255:
                num_len += 8
            elif not get_len:
                # 从高位找1
                len_end = 0
                if byte_id == 0:
                    startbit = bitid
                else:
                    startbit = 0
                for j in range(startbit, 8):
                    if (1 << (7 - j)) <= now_num:
                        now_num -= (1 << (7 - j))
                        num_len += 1
                    else:
                        len_end = j + 1
                        get_len = True
                        num = 0
                        l = 0
                        if l + 8 - len_end < num_len:
                            num += now_num
                            l += 8 - len_end
                        else:
                            rl = 8 - len_end - num_len
                            lastbit = len_end + num_len
                            num += now_num >> rl
                            num += 1 << num_len
                            lb = code if lastbit < 8 else None
                            return num, lastbit % 8, lb
                        break
            else:
                if l + 8 < num_len:
                    l += 8
                    num = (num << 8) + code
                else:
                    needl = num_len - l
                    rl = 8 - needl
                    lastbit = needl
                    num = (num << needl) + (now_num >> rl)
                    num += 1 << num_len
                    lb = code if lastbit < 8 else None
                    return num, lastbit % 8, lb
            byte_id += 1
    lb = None
    df, nbit_id, lb = decode_pos(lb, bias_id)
    index = []
    index.append(df)
    real_id = 0
    for i in range(df):
        docid, nbit_id, lb = decode_pos(lb, nbit_id)
        tf, nbit_id, lb = decode_pos(lb, nbit_id)
        if i == 0:
            real_id = docid
        else:
            real_id += docid
        index.append([real_id, tf])
    return index

# 对倒排索引分块压缩，防止爆内存
def index_encode(args, blocksize=2):
    cpn_dir = args.cpn_dir
    index_path = cpn_dir + 'Index_SPIMI.txt'
    encode_path = cpn_dir + 'encode_index.txt'
    dict_path = cpn_dir + 'dict.txt'
    index_file = open(index_path, 'r', encoding='utf-8')
    encode_index_file = open(encode_path, 'wb')
    dict_file = open(dict_path, 'w', encoding='utf-8')
    numlist = []
    word_dict = []
    lastcode = ''
    lastbias = 0
    print("Encode Index Start")
    print("Load words start")
    step = 0
    for line in index_file:
        print("Words %d/%d loaded" % (step, 246384))
        step += 1
        word_index_dict = json.loads(line)
        for key, value in word_index_dict.items():
            word_dict.append(key)
            df = value[0]
            numlist.append(df)
            for i in range(df):
                if i == 0:
                    lastid = int(value[i + 1][0])
                    docid_margin = lastid
                else:
                    docid_margin = int(value[i + 1][0]) - lastid
                    lastid = int(value[i + 1][0])
                if docid_margin <= 0:
                    raise ValueError("Docid must the growing sequence")
                numlist.append(docid_margin)
                numlist.append(int(value[i + 1][1]))
        if step % blocksize == 0:
            # 编码并写入
            biaslist, lastcode, lastbias = Gamma_encode_all(numlist, encode_index_file, lastcode, lastbias)
            assert len(word_dict) == len(biaslist)
            for i in range(len(biaslist)):
                bias_dict = dict()
                bias_dict[word_dict[i]] = biaslist[i]
                dict_file.write(json.dumps(bias_dict) + '\n')
            word_dict = []
            numlist = []

    biaslist, lastcode, lastbias = Gamma_encode_all(numlist, encode_index_file, lastcode, lastbias, True)
    assert len(word_dict) == len(biaslist)
    for i in range(len(biaslist)):
        bias_dict = dict()
        bias_dict[word_dict[i]] = biaslist[i]
        dict_file.write(json.dumps(bias_dict) + '\n')
    index_file.close()
    encode_index_file.close()
