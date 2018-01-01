# -*- coding: utf-8 -*-
import re
import os
import nltk
import json

Porter = nltk.PorterStemmer()
WNL = nltk.WordNetLemmatizer()
Stop_Words = nltk.corpus.stopwords.words('english')
MIN_DOCID = 13900


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
        out_file.write(' '.join(tokens) + '\n')
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
    len_file = open(args.cpn_dir + 'doclen.txt', 'w', encoding='utf-8')
    vocab = dict()
    doc_sum = 0
    doc_len = dict()
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
                    doc_len[doc_sum] = doc_termsum
                    doc_termsum = 0
                doc_sum += 1

            if word in vocab.keys():
                token_sum += 1
                doc_termsum += 1
    doc_len[doc_sum] = doc_termsum
    ave_doclen = sum(doc_len.values()) / doc_sum
    term_str = "词项数量:" + str(term_sum)
    docsum_str = "文档数量:" + str(doc_sum)
    token_str = "词条数量:" + str(token_sum)
    ave_str = "文档平均长度:" + str(ave_doclen)
    doclen_str = "文档长度:" + str(doc_len)
    print(term_str)
    print(docsum_str)
    print(token_str)
    print(ave_str)
    info_file.write(term_str + '\n')
    info_file.write(docsum_str + '\n')
    info_file.write(token_str + '\n')
    info_file.write(ave_str + '\n')
    len_file.write(json.dumps(doc_len))
    data_file.close()
    vocab_file.close()
    info_file.close()
    len_file.close()


# 统计Trec数据集文档数目,和docid范围
def statistic_trec(path):
    dir_list = os.listdir(path)
    doc_sum = 0
    min_id = 900000
    max_id = -1
    for dir in dir_list:
        d_path = path + '/' + dir
        if os.path.isdir(d_path):
            dir1_list = os.listdir(d_path)
            for dir1 in dir1_list:
                file_list = os.listdir(d_path + '/' + dir1)
                for file in file_list:
                    id = int(file.split('.')[0])
                    doc_sum += 1
                    max_id = max(max_id, id)
                    min_id = min(min_id, id)
    print("Doc Sum: %d" % doc_sum)  # 733328
    print("Min id: %d" % min_id)  # 13900
    print("Max id: %d" % max_id)  # 3896981


# 统计Trec数据集每个topic反馈馈的文档数目,以及相关的文档数目
def cal_topk():
    data_file = open("Data/Trec/qrels-treceval-2014.txt", 'r', encoding='utf-8')
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
        print("%d : %d" % (q, t))


# 过滤Trec数据集
def filter_trec(xml_path, out_file, op_lower=True, op_root=True, op_stop=True):
    """
    取出nxml中主title,去除所有标签，去除内容里的url
    并将文本规范化，1.统一小写 2.去停用词 3.词干提取 4.词形归并 5.分词
    """

    file = open(xml_path, 'r', encoding='utf-8')
    n_line = ''
    docid = xml_path.split('/')[-1].split('.')[0]
    docid = int(docid) - MIN_DOCID + 1
    for line in file:
        # 提取主标题
        title = re.findall(r'<article-title>.+?</article-title>', line)
        if len(title) > 0:
            title = re.sub(r'<.+?>', ' ', title[0])
            title = re.sub(r'\W+', ' ', title)
            n_line += (title + ' ')
        psg = re.findall(r'<p>.+?</p>', line)
        for p in psg:
            # 去中括号的reference
            p = re.sub(r'\[.+?\]', ' ', p)
            p = re.sub(r'<.+?>', ' ', p)
            # 去链接、字符
            p = re.sub(r'[a-zA-z]+://[^\s]*', ' ', p)
            p = re.sub(r'\W+', ' ', p)
            n_line += (p + ' ')
        if op_lower:
            n_line = n_line.lower()
        tokens = nltk.word_tokenize(n_line)
        if op_stop:
            t = len(tokens) - 1
            while t >= 0:
                # 删除停用词和x0开头的字符
                isx0 = re.fullmatch(r'x0.*', tokens[t])
                if tokens[t] in Stop_Words or isx0 is not None:
                    del tokens[t]
                t -= 1
        if op_root:
            # 归并、还原词干
            for i in range(len(tokens)):
                tokens[i] = Porter.stem(tokens[i])
                tokens[i] = WNL.lemmatize(tokens[i])
        out_file.write(str(docid) + '\t' + ' '.join(tokens) + '\n')

    file.close()

# 计算Trec文档长度和平均长度
def get_doclen(args):
    data_path = args.data_pro_dir + 'docset.txt'
    out_path = args.cpn_dir + 'doclen.txt'
    data_file = open(data_path, 'r', encoding='utf-8')
    out_file = open(out_path, 'w', encoding='utf-8')
    doclen = dict()
    step = 0
    print("Cal Trec doclen")
    for line in data_file:
        print("Process : %d/%d" % (step, 733328))
        seq = line.strip('\n').split('\t')
        words = seq[1].split(' ')
        doclen[seq[0]] = len(words)
        step += 1
    print("Cal Trec doclen finished")
    doclen_str = json.dumps(doclen)
    out_file.write(doclen_str)
    data_file.close()
    out_file.close()

# 提取Topic中的summary域
def get_summary(args):
    trec2014 = open(args.data_pro_dir + 'topics2014.xml', 'r', encoding='utf-8')
    out2014 = open(args.data_pro_dir +'summary2014.txt', 'w', encoding='utf-8')
    for line in trec2014:
        if '<summary>' in line:
            mysum = re.sub(r'<.+?>', '', line)
            mysum = mysum.lower()
            tokens = nltk.word_tokenize(mysum)
            t = len(tokens) - 1
            while t >= 0:
                # 删除停用词和x0开头的字符
                isword = re.fullmatch(r'[a-z]+', tokens[t])
                if tokens[t] in Stop_Words or isword is None:
                    del tokens[t]
                t -= 1
                # 归并、还原词干
                for i in range(len(tokens)):
                    tokens[i] = Porter.stem(tokens[i])
                    tokens[i] = WNL.lemmatize(tokens[i])
            out2014.write(' '.join(tokens) + '\n')
    trec2014.close()
    out2014.close()
    trec2015 = open(args.data_pro_dir + 'topics2015A.xml', 'r', encoding='utf-8')
    out2015 = open(args.data_pro_dir + 'summary2015.txt', 'w', encoding='utf-8')
    for line in trec2015:
        if '<summary>' in line:
            mysum = re.sub(r'<.+?>', '', line)
            mysum = mysum.lower()
            tokens = nltk.word_tokenize(mysum)
            t = len(tokens) - 1
            while t >= 0:
                # 删除停用词和x0开头的字符
                isword = re.fullmatch(r'[a-z]+', tokens[t])
                if tokens[t] in Stop_Words or isword is None:
                    del tokens[t]
                t -= 1
                # 归并、还原词干
                for i in range(len(tokens)):
                    tokens[i] = Porter.stem(tokens[i])
                    tokens[i] = WNL.lemmatize(tokens[i])
            out2015.write(' '.join(tokens) + '\n')
    trec2015.close()
    out2015.close()
