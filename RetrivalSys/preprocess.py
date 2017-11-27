import re

# 合并剧本
def merge_data():
    data_file1 = open("../Data/Drama/shakespeare-merchant.trec.1", 'r', encoding='utf-8')
    data_file2 = open("../Data/Drama/shakespeare-merchant.trec.2", 'r', encoding='utf-8')
    out_file = open("../Data/Drama/shakespeare-merchant", 'w', encoding='utf-8')
    lines = data_file1.readlines()
    out_file.writelines(lines)
    lines = data_file2.readlines()
    out_file.writelines(lines)
    data_file2.close()
    data_file1.close()
    out_file.close()



# 去标签,把非字符替换成空格,去除多余空格
def del_label(data_path):
    data_file = open(data_path, 'r', encoding='utf-8')
    out_file = open(data_path + "_nolabel", 'w', encoding='utf-8')
    for line in data_file:
        while re.match(r'<.+?>', line):
            line = re.sub(r'<.+?>', '', line)
        if line == "\n":
            continue
        line = re.sub(r'\W+', ' ', line)
        out_file.write(line+'\n')
    data_file.close()
    out_file.close()

# 制作vocab
def make_vocab(data_path, out_path):
    data_file = open(data_path, 'r', encoding='utf-8')
    vocab_file = open(out_path, 'w', encoding='utf-8')
    vocab = dict()
    for line in data_file:
        line = line.strip('\n')
        words = line.split(' ')
        for wrd in words:
            isnum = re.fullmatch(r'\d+', wrd)
            if isnum is None:
                if wrd not in vocab.keys():
                    vocab[wrd] = 1
                else:
                    vocab[wrd] += 1
    vocab = sorted(vocab.items(), key=lambda e: e[0], reverse=False)
    del vocab[0]
    for item in vocab:
        vocab_file.write(item[0] + ' ' + str(item[1]) + '\n')
    data_file.close()
    vocab_file.close()


# 统计信息
def statistic_info():
    data_file = open("../Data/Drama/shakespeare-merchant_nolabel", 'r', encoding='utf-8')
    vocab_file = open("components/vocab_ori.txt", 'r', encoding='utf-8')
    info_file = open("components/statistic_res.txt", 'w', encoding='utf-8')
    vocab = dict()
    doc_sum = 0
    doc_len = []
    term_sum = 0
    token_sum = 0
    for line in vocab_file:
        line = line.strip('\n')
        seq = line.split(' ')
        vocab[seq[0]] = int(seq[1])
        term_sum += 1

    doc_termsum = 0
    for line in data_file:
        line = line.strip('\n')
        seq = line.split(' ')
        for word in seq:
            if word == 'SHK':
                if doc_sum > 0:
                    doc_len.append(doc_termsum)
                doc_termsum = 0
                doc_sum += 1

            if word in vocab.keys():
                token_sum += 1
                doc_termsum += 1
    ave_doclen = sum(doc_len) / doc_sum
    term_str = "词项数量:" + str(term_sum)
    docsum_str = "文档数量:" + str(doc_sum)
    token_str = "词条数量:" + str(token_sum)
    ave_str = "文档平均长度:" + str(ave_doclen)
    print(term_str)
    print(docsum_str)
    print(token_str)
    print(ave_str)
    info_file.write(term_str + '\n')
    info_file.write(docsum_str + '\n')
    info_file.write(token_str + '\n')
    info_file.write(ave_str + '\n')
    data_file.close()
    vocab_file.close()
    info_file.close()



# merge_data()
# del_label("../Data/Drama/shakespeare-merchant")
# make_vocab("../Data/Drama/shakespeare-merchant_nolabel")
# statistic_info()