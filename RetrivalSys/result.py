import math
import linecache
from RetrivalSys import Btree_search
from RetrivalSys import compress

PARAM_K1 = 1.5
PARAM_B = 0.75
EPSILON = 0.25
#BTree = Btree_search.createTree(args)


# 输入查询词得到倒排记录表
def GetResult(args, BTree, query):
    bias = Btree_search.FindWord(BTree, query)
    no_index_list = []
    if bias is False:
        return no_index_list
    else:
        index_list = compress.Gamma_decode_all(args, bias)
        return index_list


'''
corpus = [];
def CalBM25():
    bm25Model = bm25.BM25(corpus)
    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
    query_str = '高血压 患者 药物'
    query = []
    for word in query_str.strip().split():
        query.append(word.decode('utf-8'))
    scores = bm25Model.get_scores(query, average_idf)
    # scores.sort(reverse=True)
    print(scores)
'''


def CalBM25(query_str, docid, doc_sum, avgdl, doc_len, word_dict):
    query = {}
    score = 0
    tf = 0
    words = query_str.strip().split()
    #计算query内的词频
    for word in words:
        if word not in query:
            query[word] = 0
        query[word] += 1
    for word in words:
        if len(word_dict[word]) == 0:
            tf = 0
            idf = 0
        else:
            index_list = word_dict[word]
            df = index_list[0]
            idf = math.log(doc_sum - df + 0.5) - math.log(df + 0.5)
            for i in range(df):
                if docid == index_list[i + 1][0]:
                    tf = index_list[i + 1][1]
            if i == df:
                tf = 0
        #增加了词在query中词频
        score += query[word] * idf * tf * (PARAM_K1 + 1) / (
        tf + PARAM_K1 * (1 - PARAM_B + PARAM_B * int(doc_len[docid - 1]) / avgdl))
        # 不考虑词在query中词频
        #score += idf * tf * (PARAM_K1 + 1) / (tf + PARAM_K1 * (1 - PARAM_B + PARAM_B * int(doc_len[docid - 1]) / avgdl))
    return score


def GetTopK(args, BTree, query_str, K):
    scores = {}
    docids = []
    word_dict = {}
    doc_len = []
    words = query_str.strip().split()
    line = linecache.getline(args.data_ori_dir+"statistic_res.txt",2).strip('\n')
    seq = line.split(':')
    doc_sum = int(seq[1])
    line = linecache.getline(args.data_ori_dir + "statistic_res.txt", 4).strip('\n')
    seq = line.split(':')
    avgdl = float(seq[1])
    line = linecache.getline(args.data_ori_dir + "statistic_res.txt", 5).strip('\n')
    seq = line.split(':')
    s = seq[1].replace(' ', '')
    s = s.replace('[', '')
    s = s.replace(']', '')
    doc_len = s.split(',')
    for word in words:
        index_list = GetResult(args, BTree, word)
        if len(index_list) == 0:
            word_dict[word] = {}
        else:
            for i in range(index_list[0]):
                doc = index_list[i + 1][0]
                if doc not in docids:
                    docids.append(index_list[i + 1][0])
            word_dict[word] = index_list
    for docid in docids:
        score = CalBM25(query_str, docid, doc_sum, avgdl, doc_len, word_dict)
        scores[docid-1] = score
    dict = sorted(scores.items(), key=lambda d: d[1], reverse=True)
    for i in range(K):
        print(dict[i])


#print(GetResult("paak"))
#print(GetResult("add"))
#GetTopK("park add", 2)
