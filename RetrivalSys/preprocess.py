# -*- coding: utf-8 -*-
import re
import os
import nltk
from bs4 import BeautifulSoup

# 合并剧本
def merge_data(args, file_name1, file_name2):
    dir_path = args.data_ori_dir
    data_file1 = open(dir_path + file_name1, 'r', encoding='utf-8')
    data_file2 = open(dir_path + file_name2, 'r', encoding='utf-8')
    out_file = open(dir_path + "shakespeare-merchant", 'w', encoding='utf-8')
    lines = data_file1.readlines()
    out_file.writelines(lines)
    lines = data_file2.readlines()
    out_file.writelines(lines)
    data_file2.close()
    data_file1.close()
    out_file.close()

# 去标签,把非字符替换成空格,去除多余空格
def del_label(args, file_name):
    dir_path = args.data_ori_dir
    data_path = dir_path + file_name
    data_file = open(data_path, 'r', encoding='utf-8')
    out_file = open(data_path + "_nolabel", 'w', encoding='utf-8')
    for line in data_file:
        line = re.sub(r'<.+?>', '', line)
        line = re.sub(r'\W+', ' ', line)
        if line == " ":
            continue
        tokens = nltk.word_tokenize(line)
        out_file.write(' '.join(tokens)+'\n')
    data_file.close()
    out_file.close()

# 制作vocab
def make_vocab(args, file_name, out_name):
    dir_path = args.data_ori_dir
    data_path = dir_path + file_name
    out_path = dir_path + out_name
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
def statistic_info(args):
    dir_path = args.data_ori_dir
    data_file = open(dir_path + "shakespeare-merchant_nolabel", 'r', encoding='utf-8')
    vocab_file = open(dir_path + "vocab_ori.txt", 'r', encoding='utf-8')
    info_file = open(dir_path + "statistic_res.txt", 'w', encoding='utf-8')
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

# 提取summary域,统计文档数目
def get_summary(path):
    out_dir = "../Data/Trec/"
    dir_list = os.listdir(path)
    doc_set = set()
    for dir in dir_list:
        d_path = path + '/' + dir
        if os.path.isdir(d_path):
            dir1_list = os.listdir(d_path)
            for dir1 in dir1_list:
                file_list = os.listdir(d_path + '/' + dir1)
                for file in file_list:
                    doc_set.add(file)
                    out_file = out_dir + file.split('.')[0]
                    # with open(file, 'r', encoding='utf-8'):
                    #     for line in file:



    print("Doc Sum: %d" % len(doc_set))




def cal_topk():
    data_file = open("../Data/Trec/qrels-treceval-2014.txt", 'r', encoding='utf-8')
    q_dict = dict()
    for line in data_file:
        seq = line.strip('\n').split('\t')
        q_id = int(seq[0])
        r = int(seq[3])
        if r > 0:
            if q_id not in q_dict.keys():
                q_dict[q_id] = 1
            else:
                q_dict[q_id] += 1

    data_file.close()
    for q, t in q_dict.items():
        print("%d : %d" %(q, t))

def filter_trec(op_lower=False, op_root=False, op_stop=False):
    """
    取出nxml中主title,并且从Conclusion的内容后截断，只保留前部分
    并将文本规范化，1.统一小写 2.去停用词 3.词干提取 4.词形归并 5.分词
    """

    file = open("../Data/Trec/3148967.nxml", 'r', encoding='utf-8')
    out_file = open("../Data/Trec/3148967_res.txt", 'w', encoding='utf-8')
    # porter = nltk.PorterStemmer()
    # wnl = nltk.WordNetLemmatizer()
    # tn = nltk.word_tokenize()
    for line in file:
        # line = re.sub(r'<.+?>', ' ', line)
        # line = ' '.join(line.split()[12:])
        title = re.findall(r'<article-title>.+?</article-title>', line)
        psg = re.findall(r'<p>.+?</p>', line)
        psg = re.sub(r'<.+?>', ' ', title[0] + '\n' + '\n'.join(psg))
        n_line = ' '.join(psg.split())
        out_file.write(n_line)
    file.close()
    out_file.close()
# merge_data()
# del_label("../Data/Drama/shakespeare-merchant")
# make_vocab("../Data/Drama/shakespeare-merchant_nolabel", "components/vocab_ori.txt")
# statistic_info()

# dir_path = os.path.expanduser('~') + "/Documents/Data/TrecCDS2014"
# get_summary(dir_path)
# cal_topk()
# filter_trec()