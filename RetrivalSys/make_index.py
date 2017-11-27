import re
import json
import os
import queue



# 给优先队列的自定义结构
class Term(object):
    def __init__(self, word, index_list, id):
        self.word = word
        self.index_list = index_list
        self.id = id

    def __lt__(self, other):  # operator <
        if self.word == other.word:
            return self.index_list[1][0] < other.index_list[1][0]
        return self.word < other.word


# 查看剩余内存:
def check_memory():
    with open('/proc/meminfo') as fd:
        for line in fd:
            if line.startswith('MemTotal'):
                total = line.split()[1]
                continue
            if line.startswith('MemFree'):
                free = line.split()[1]
                break

    FreeMem = int(free) / 1024.0
    TotalMem = int(total) / 1024.0
    print("FreeMem:" + "%.2f" % FreeMem + 'M')
    print("TotalMem:" + "%.2f" % TotalMem + 'M')
    print("FreeMem/TotalMem:" + "%.2f" % ((FreeMem / TotalMem) * 100) + '%')
    return FreeMem

# 从字典获取第一行key和value, 这里用json格式导致仅有一个term
def getkeyitem(termdict):
    for key, value in termdict.items():
        return key, value


# SPIMI
# 后期用到bm25,需要保存词的df,文档中的tf
def SPIMI(data_path, block):
    block_size = block
    data_file = open(data_path, 'r', encoding='utf-8')
    local_index = dict()
    doc_id = 0
    index_sum = 0
    block_id = 1
    for line in data_file:
        terms = line.strip('\n').split(' ')
        if index_sum > block_size:
            # 写入文件
            block_file = open("components/block" + str(block_id), 'w', encoding='utf-8')
            sorted_index = sorted(local_index.items(), key=lambda e: e[0])
            for item in sorted_index:
                key_dict = {item[0]: item[1]}
                json_str = json.dumps(key_dict)
                block_file.write(json_str + '\n')
            local_index = dict()
            block_id += 1
            index_sum = 0

        for term in terms:
            if term == '':
                continue
            if term == 'SHK':
                doc_id += 1
            # 忽略纯数字词项
            isnum = re.fullmatch(r'[0-9]+', term)
            if isnum is not None:
                continue
            if term in local_index.keys():
                # 已有词项，增加索引

                if doc_id == local_index[term][-1][0]:
                    local_index[term][-1][1] += 1
                else:
                    local_index[term].append([doc_id, 1])
                    local_index[term][0] += 1
                    index_sum += 1

            else:
                # 新建立该词项的索引
                local_index[term] = list()
                local_index[term].append(1)
                local_index[term].append([doc_id, 1])
                index_sum += 1
    if index_sum > 0:
        # 写入文件
        block_file = open("components/block" + str(block_id), 'w', encoding='utf-8')
        sorted_index = sorted(local_index.items(), key=lambda e: e[0])
        for item in sorted_index:
            key_dict = {item[0]: item[1]}
            json_str = json.dumps(key_dict)
            block_file.write(json_str + '\n')
    data_file.close()

    # 合并各个块,使用优先队列进行多路合并
    path_list = os.listdir("components/")
    block_lists = []
    for path in path_list:
        if path.startswith('block'):
            block_lists.append(path)
    block_lists.sort()
    term_queue = queue.PriorityQueue()

    # 设置N路合并,暂时设定为总块数，一次合并
    merge_N = len(block_lists)
    block_files = list()
    for i in range(merge_N):
        block_file = open("components/" + block_lists[i], 'r', encoding='utf-8')
        block_files.append(block_file)
    out_file = open("components/Index_SPIMI.txt", 'w', encoding='utf-8')
    merged_flag = [False for i in range(merge_N)]
    end_file = 0
    while end_file < merge_N:
        for i in range(merge_N):
            if not merged_flag[i]:
                line = block_files[i].readline()
                merged_flag[i] = True
                if not line:
                    end_file += 1
                    merged_flag[i] = True
                else:
                    term = json.loads(line)
                    key, value = getkeyitem(term)
                    term = Term(key, value, i)
                    term_queue.put(term)
        if not term_queue.empty():
            first_term = term_queue.get()
            merged_flag[first_term.id] = False
        while not term_queue.empty():
            top_term = term_queue.get()
            if top_term.word == first_term.word:
                # 进行合并
                if first_term.index_list[-1][0] < top_term.index_list[1][0]:
                    first_term.index_list[0] += top_term.index_list[0]
                    for item in top_term.index_list[1:]:
                        first_term.index_list.append(item)
                else:
                    first_term.index_list[0] += top_term.index_list[0] - 1
                    first_term.index_list[-1][1] += top_term.index_list[1][1]
                    for item in top_term.index_list[1:]:
                        first_term.index_list.append(item)
                merged_flag[top_term.id] = False
            else:
                term_queue.put(top_term)
                # 写入文件
                term_dict = {first_term.word: first_term.index_list}
                term_str = json.dumps(term_dict)
                out_file.write(term_str + '\n')
                break
        if term_queue.empty():
            # 写入文件
            term_dict = {first_term.word: first_term.index_list}
            term_str = json.dumps(term_dict)
            out_file.write(term_str + '\n')




    # for i in range(len(block_lists)):
    #     block_file = open("components/" + block_lists[i], 'r', encoding='utf-8')
    #     new_file = open("components/merged" + str(i), 'w', encoding='utf-8')
    #     m_line = merged_file.readline()
    #     print(i)
    #     while m_line:
    #         m_term = json.loads(m_line)
    #         b_line = block_file.readline()
    #         if not b_line:
    #             while m_line:
    #                 new_file.write(m_line)
    #                 m_line = merged_file.readline()
    #             break
    #         b_term = json.loads(b_line)
    #         for key in b_term.keys():
    #             b_key = key
    #         for key in m_term.keys():
    #             m_key = key
    #         if m_key == b_key:
    #             tf = b_term[b_key][0]
    #             sameid = 0
    #             # 检查收尾是否docid一致
    #
    #             for block_index in b_term[b_key][1:]:
    #                 m_term[m_key].append(block_index)
    #             m_str = json.dumps(m_term)
    #             new_file.write(m_str + '\n')
    #         elif m_key > b_key:
    #             new_file.write(b_line)
    #             new_file.write(m_line)
    #         else:
    #             new_file.write(m_line)
    #             new_file.write(b_line)
    #         m_line = merged_file.readline()
    #     b_line = block_file.readline()
    #     while b_line:
    #         new_file.write(b_line)
    #         b_line = block_file.readline()
    #     merged_file.close()
    #     new_file.close()
    #     block_file.close()
    #     merged_file = open("components/merged" + str(i), 'r', encoding='utf-8')


# SPIMI("../Data/Drama/shakespeare-merchant_nolabel", 1000)
