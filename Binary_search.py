from  RetrivalSys import Btree_search




#二分查找
#在lines寻找word，返回对应偏移量
def FindWord(word, lines, lines_num):
    low = 0
    high = lines_num - 1

    while low <= high:
        mid = (low + high) // 2
        line = lines[mid]
        pre = line.split('*')[0]
        len_pre = len(pre)
        if Btree_search.cmp_key(word, line) == -1:
            high = mid - 1
        elif Btree_search.cmp_key(word, line) == -2:
            low = mid + 1
        else:
            return Btree_search.cmp_key(word, line)

