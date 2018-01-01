'''
    查询单词对应的倒排记录表，进行bm25的计算
'''
import math
from RetrivalSys import Btree_search
from RetrivalSys import compress

PARAM_K1 = 1.5
PARAM_B = 0.75
EPSILON = 0.25

# 输入构建好的B输，和查询词得到倒排记录表
def GetResult(args, BTree, query):
    bias = Btree_search.FindWord(BTree, query)
    no_index_list = []
    if bias is None:
        return no_index_list
    else:
        index_list = compress.Gamma_decode_all(args, bias)
        return index_list

# 从语料中计算bm25，并返回值最高的K个(docid,bm25)对
def GetTopK(args, BTree, query_str, doc_len, K):
    scores = {}
    qwords = query_str.strip('\n').split(' ')
    qword_dict = {}
    for wrd in qwords:
        if wrd not in qword_dict.keys():
            qword_dict[wrd] = 1
        else:
            qword_dict[wrd] += 1

    doc_sum = len(doc_len)
    avgdl = sum(doc_len.values()) / doc_sum
    for word, qtf in qword_dict.items():
        index_list = GetResult(args, BTree, word)
        if len(index_list) > 0:
            df = index_list[0]
            for i in range(df):
                doc = index_list[i + 1][0]
                tf = index_list[i + 1][1]
                if doc not in scores.keys():
                    scores[doc] = calbm25(word, qword_dict[word], df, tf, doc_sum, avgdl, doc_len[str(doc)])
                else:
                    scores[doc] += calbm25(word, qword_dict[word], df, tf, doc_sum, avgdl, doc_len[str(doc)])
    topK_dict = sorted(scores.items(), key=lambda d: d[1], reverse=True)
    return topK_dict[0:K]

def calbm25(term, qtf, tf, df, doc_sum, avgdl, doc_len):
    idf = math.log(doc_sum - df + 0.5) - math.log(df + 0.5)
    score = qtf * idf * tf * (PARAM_K1 + 1) / (
        tf + PARAM_K1 * (1 - PARAM_B + PARAM_B * doc_len / avgdl))
    return score
