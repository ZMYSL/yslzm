from RetrivalSys import preprocess
from RetrivalSys import make_index
from RetrivalSys import DictBuild
from RetrivalSys import compress
from RetrivalSys import Btree_search
from RetrivalSys import result
import argparse
import os


def set_args(parser):
    """设置所有运行参数
    包括运行作业1，还是作业2，以及对应的处理方法和配置参数
    """
    runtime = parser.add_argument_group("Environment")
    runtime.add_argument('--work-task', type=str, default='Drama',
                         help='Drama is work1, Trec is work2, filter is work3')

    files = parser.add_argument_group("Filesystem")
    files.add_argument('--data-ori-dir', type=str, default='Data/Drama/',
                       help='original data dir , Trec data in other dir')
    files.add_argument('--data-pro-dir', type=str, default='Data/Drama/',
                       help='processed data dir, Drama data dir is equal to data-ori-dir')
    files.add_argument('--train-file', type=str, default='qrels-treceval-2014.txt',
                       help='train file include topic doc rel')
    files.add_argument('--cpn-dir', type=str, default='RetrivalSys/components/Drama/',
                       help='components dir')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'Information Retrival',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    set_args(parser)
    args = parser.parse_args()
    if args.work_task == 'Drama':
        preprocess.merge_data(args, 'shakespeare-merchant.trec.1', 'shakespeare-merchant.trec.2')
        preprocess.del_label(args, 'shakespeare-merchant')
        preprocess.make_vocab(args, 'shakespeare-merchant_nolabel', 'vocab_ori.txt')
        preprocess.statistic_info(args)
        make_index.SPIMI(args, 'shakespeare-merchant_nolabel', 1000)
        compress.index_encode(args)
        DictBuild.DictCompress(args)
        BTree = Btree_search.createTree(args)

        # 倒排建立、压缩、词典压缩完成，输入返回相应关键词的倒排记录
        while True:
            input_word = input("输入需要查询的单词，返回倒排记录，输入order:exit退出\n")
            if input_word == 'order:exit':
                break
            bias = Btree_search.FindWord(BTree, input_word)
            if bias == False:
                print("文档集合中没有该单词，请重新输入")
                continue
            index_list = compress.Gamma_decode_all(args, bias)
            print(index_list)


    if args.work_task == 'filter':
        path = args.data_ori_dir
        dir_list = os.listdir(path)
        filtered_sum = 0
        out_file = open(args.data_pro_dir + 'docset.txt', 'w', encoding='utf-8')
        for dir in dir_list:
            d_path = path + '/' + dir
            if os.path.isdir(d_path):
                dir1_list = os.listdir(d_path)
                for dir1 in dir1_list:
                    dir2_path = d_path + '/' + dir1
                    file_list = os.listdir(dir2_path)
                    for file in file_list:
                        file_name = file.split('.')
                        file_path = dir2_path + '/' + file
                        preprocess.filter_trec(file_path, out_file)
                        filtered_sum += 1
                        if filtered_sum % 100 == 0:
                            print("Filter process: %d/%d" %(filtered_sum, 733328))
        out_file.close()

