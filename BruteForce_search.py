from  RetrivalSys import Btree_search




#二分查找
#在lines寻找word，返回对应偏移量
def FindWord(word, lines, lines_num):
    for i in range(lines_num):
        line = lines[i]
        if Btree_search.cmp_key(word, line) is not -1 or -2:
            continue;
        else:
            return Btree_search.cmp_key(word, line)
