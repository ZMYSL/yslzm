from RetrivalSys import Btree_search
from RetrivalSys import compress

#输入查询词得到倒排记录表
def GetResult(query):
    bias = Btree_search.FindWord(2.5,query)
    index_list = compress.Gamma_decode_all(bias)
    return index_list
print(GetResult("ACT"))
