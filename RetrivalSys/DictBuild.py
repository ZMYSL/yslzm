'''
    从倒排索引文件中抽取单词建立压缩词典，存放至./components/CompressedDict.txt中
    提供解压缩方法DictDecompress
'''

import re

#参数为一个单词list，返回list中单词的最长前缀
#寻找一个单词表的最长前缀
#将这个单词表进行字母序排序，并比较第一个
def FindLongestFront(voclist):
    if len(voclist) == 0:
        return ''
    if len(voclist) == 1:
        return voclist[0]
    #找出最短字符串长度及这个字符串
    #voclist = sorted(voclist, key = lambda x: len(x))
    #在这个list中，其实只需比较第一个单词和倒数第一个单词的最长前缀即可
    length = min(len(voclist[0]), len(voclist[-1]))
    front = ''
    for i in range(length):
        if voclist[0][i] == voclist[-1][i]:
            front = front + voclist[0][i]
        else:
            break
    return front

def FindPostCode(longest_front, word):
    front_length = len(longest_front)
    return len(word) - front_length, word[front_length:]


#前端编码与后缀分隔符为'*'，后缀之间的分隔符为'$'
def FrontCoding(voclist, size_num):
    string = ''
    #寻找最长公共前缀
    longest_front = FindLongestFront(voclist)
    string = string + longest_front + '*'
    for i in range(size_num):
        #根据最长公共前缀，得出每个词的后缀与后缀长度
        length, postcode = FindPostCode(longest_front, voclist[i])
        if i == size_num - 1:
            string = string + postcode + str(length)

        else:
            string = string + postcode + str(length) + '$'
    return string

#块的大小为size_num（一个块有size_num个单词），将解压词典存放在save_file_path中
def DictCompress(size_num, save_file_path):
    with open('./components/Drama/Index_SPIMI.txt', 'r', encoding='utf-8') as lists:
        voclist = []
        with open(save_file_path,'w') as dict:
            #每size_num个单词为一个块，一起处理，并将处理结果写入到save_file_path中、
            while True:
                for i in range(size_num):
                    line = lists.readline()
                    if line == '':
                        return
                    word = line.strip('{}').split(':')[0].strip('"')
                    #print(word)
                    voclist.append(word)
                    if i == size_num - 1:
                        string = FrontCoding(voclist, size_num)
                        dict.write(string + '\n')
                        voclist.clear()
                        break

#单行解压词典
#传入参数为压缩词典字符串
def LineDecompress(line):
    dict = []
    front, rest = line.strip('\n').split('*')
    rest = rest.split('$')
    for word in rest:
        # 将word分解为字符串+数字的组合
        length = int(re.findall("\d+", word)[0])
        post = '' + word.strip(str(length))
        # 检验分解出的后缀长度是否等于记载的length，若符合则写入
        if len(post) == length:
            dict.append(front + post)
        else:
            raise NameError('Post length doesn\'t equal to length!')
    return dict

#解压词典文件
def DictDecompress(compress_file_path, decompress_file_path):
    with open(compress_file_path, 'r', encoding='utf-8') as compress_dict:
        with open(decompress_file_path, 'w', encoding='utf-8') as decompress_dict:
            while True:
                line = compress_dict.readline()
                if line == '':
                    break
                front, rest = line.strip('\n').split('*')
                rest = rest.split('$')
                for word in rest:
                    #将word分解为字符串+数字的组合
                    length = int(re.findall("\d+",word)[0])
                    post = '' + word.strip(str(length))
                    # print('post: ',post)
                    # print('length:' ,length)
                    # print('len_post:',len(post))
                    #检验分解出的后缀长度是否等于记载的length，若符合则写入
                    if len(post) == length:
                        decompress_dict.write(front + post + '\n')
                    else:
                        raise NameError('Post length doesn\'t equal to length!' )

#DictCompress(4, './components/CompressedDict.txt')
#DictDecompress('./components/CompressedDict.txt', './components/DecompressedDict.txt')
