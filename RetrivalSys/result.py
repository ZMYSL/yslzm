import math
from RetrivalSys import Btree_search
from RetrivalSys import compress

PARAM_K1 = 1.5
PARAM_B = 0.75
EPSILON = 0.25

#输入查询词得到倒排记录表
def GetResult(query):
    bias = Btree_search.FindWord(2.5,query)
    index_list = compress.Gamma_decode_all(bias)
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

def CalBM25(query_str,docid):
    query = {}
    score=0
    doc_sum=0
    avgdl=0
    tf=0
    doc_len=[]
    words=query_str.strip().split()
    statistic_res = open("../Data/Drama/statistic_res.txt", 'r')
    k=0
    for line in statistic_res:
        line = line.strip('\n')
        seq = line.split(':')
        if k==1:
            doc_sum = int(seq[1])
        if k==3:
            avgdl = float(seq[1])
        if k==4:
            s = seq[1].replace(' ', '')
            s = s.replace('[', '')
            s = s.replace(']', '')
            doc_len = s.split(',')
        k += 1
    for word in words:
        if word not in query:
            query[word] = 0
        query[word] += 1
    for word in words:
        index_list = GetResult(word)
        df = index_list[0]
        idf = math.log(doc_sum - df + 0.5) - math.log(df + 0.5)
        for i in range(df):
            if docid==index_list[i+1][0]:
                tf=index_list[i+1][1]
        if i == df:
            tf = 0
        score += query[word]*idf * tf * (PARAM_K1 + 1) / (tf + PARAM_K1 * (1 - PARAM_B + PARAM_B * int(doc_len[docid-1]) / avgdl))
    return score

def GetTopK(query_str,K):
    scores = {}
    docids = []
    words = query_str.strip().split()
    for word in words:
        index_list = GetResult(word)
        for i in range(index_list[0]):
            doc = index_list[i+1][0]
            if doc not in docids:
                docids.append(index_list[i+1][0])
    for docid in docids:
        score = CalBM25(query_str, docid)
        scores[docid] = score
    dict = sorted(scores.items(), key=lambda d: d[1], reverse=True)
    for i in range(K):
        print(dict[i])

GetTopK("park add",2)



