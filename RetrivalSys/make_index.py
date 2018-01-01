'''
    实现SPIMI索引构建算法，主要函数SPIMI()
'''
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

    def __lt__(self, other):  # operator < :按字典序一级排序，按第一个倒排记录的docid进行二级排序
        if self.word == other.word:
            return self.index_list[1][0] < other.index_list[1][0]
        return self.word < other.word

# 从字典获取第一行key和value, 这里用json格式导致仅有一个term
def getkeyitem(termdict):
    for key, value in termdict.items():
        return key, value


# SPIMI
# 后期用到bm25,需要保存词的df,文档中的tf
def SPIMI(args, file_name, block, isDrama=True, minDF=0):
    """SPIMI索引构建:分块构建索引，然后用优先队列一次合并，减少中间文件
        同时进行单词过滤，剔除df小于minDF的词，过滤Trec上的奇怪字符和单词
                    Args:
                        args:参数配置
                        file_name:需要打开的数据集名称
                        block:一个块存储的倒排记录条数，当某篇doc构建完数量大于block后进行写入
                        isDrama:区分是shakespeare数据集还是Trec数据集，细节处理不同
                        minDF:进行单词过滤，df小于mindf的单词被剔除
                    Output:
                        在args指定的路径中生成中间文件block%id和合并后的最终索引文件Index_SPIMI.txt
                    """
    block_size = block
    dir_path = args.data_pro_dir
    cpn_path = args.cpn_dir
    data_path = dir_path + file_name
    data_file = open(data_path, 'r', encoding='utf-8')
    local_index = dict()
    doc_id = 0
    index_sum = 0
    block_id = 1
    step = 0
    print("SPIMI work start")
    if isDrama:
        for line in data_file:
            terms = line.strip('\n').split(' ')
            if index_sum > block_size:
                # 写入文件
                block_file = open(cpn_path + "block" + str(block_id), 'w', encoding='utf-8')
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
            block_file = open(cpn_path + "block" + str(block_id), 'w', encoding='utf-8')
            sorted_index = sorted(local_index.items(), key=lambda e: e[0])
            for item in sorted_index:
                key_dict = {item[0]: item[1]}
                json_str = json.dumps(key_dict)
                block_file.write(json_str + '\n')
        data_file.close()
    else:
        for line in data_file:
            if step % 100 == 0:
                print("Process : %d/%d" % (step, 733328))
            step += 1
            seq = line.strip('\n').split('\t')
            doc_id = int(seq[0])
            if index_sum > block_size:
                # 写入文件
                print("Write block %d" % block_id)
                block_file = open(cpn_path + "block" + str(block_id), 'w', encoding='utf-8')
                sorted_index = sorted(local_index.items(), key=lambda e: e[0])
                for item in sorted_index:
                    df = item[1][0]
                    index_sorted = sorted(item[1][1:df + 1], key=lambda e: e[0])
                    index_sorted.insert(0, df)
                    key_dict = {item[0]: index_sorted}
                    json_str = json.dumps(key_dict)
                    block_file.write(json_str + '\n')
                local_index = dict()
                block_id += 1
                index_sum = 0
                print("Write block finished")

            for term in seq[1].split(' '):
                isword = re.fullmatch(r'[a-z]+', term)
                if isword is None:
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
            block_file = open(cpn_path + "block" + str(block_id), 'w', encoding='utf-8')
            sorted_index = sorted(local_index.items(), key=lambda e: e[0])
            for item in sorted_index:
                df = item[1][0]
                index_sorted = sorted(item[1][1:df + 1], key=lambda e: e[0])
                index_sorted.insert(0, df)
                key_dict = {item[0]: index_sorted}
                json_str = json.dumps(key_dict)
                block_file.write(json_str + '\n')
        data_file.close()
    # 合并各个块,使用优先队列进行多路合并
    path_list = os.listdir(cpn_path)
    block_lists = []
    for path in path_list:
        if path.startswith('block'):
            block_lists.append(path)
    block_lists.sort()
    term_queue = queue.PriorityQueue()

    # 设置N路合并,暂时设定为所有块一起合并
    merge_N = len(block_lists)
    block_files = list()
    print("Merge Index start")
    for i in range(merge_N):
        block_file = open(cpn_path + block_lists[i], 'r', encoding='utf-8')
        block_files.append(block_file)
    out_file = open(cpn_path + "Index_SPIMI.txt", 'w', encoding='utf-8')
    merged_flag = [False for i in range(merge_N)]
    end_file = 0
    step = 0
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
                first_i = 1
                top_i = 1
                while first_i < len(first_term.index_list) and top_i < len(top_term.index_list):
                    if first_term.index_list[first_i][0] == top_term.index_list[top_i][0]:
                        first_term.index_list[first_i][1] += top_term.index_list[top_i][1]
                        top_i += 1
                        first_i += 1
                    elif first_term.index_list[first_i][0] < top_term.index_list[top_i][0]:
                        first_i += 1
                    else:
                        first_term.index_list.insert(first_i, top_term.index_list[top_i])
                        top_i += 1
                        first_i += 1
                while top_i < len(top_term.index_list):
                    first_term.index_list.append(top_term.index_list[top_i])
                    top_i += 1
                first_term.index_list[0] = len(first_term.index_list) - 1
                merged_flag[top_term.id] = False
            else:
                term_queue.put(top_term)
                # 写入文件
                if first_term.index_list[0] <= minDF:
                    break
                term_dict = {first_term.word: first_term.index_list}
                term_str = json.dumps(term_dict)
                out_file.write(term_str + '\n')
                print("%d word %s writed" % (step, first_term.word))
                step += 1
                break
        if end_file >= merge_N:
            break
        if term_queue.empty():
            # 写入文件
            if first_term.index_list[0] <= minDF:
                continue
            term_dict = {first_term.word: first_term.index_list}
            term_str = json.dumps(term_dict)
            out_file.write(term_str + '\n')
            print("%d word %s writed" % (step, first_term.word))
            step += 1
    out_file.close()

