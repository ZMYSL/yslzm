import sys
import argparse
from RetrivalSys import preprocess
from RetrivalSys import make_index
from RetrivalSys import DictBuild


def set_args(parser):
    """设置所有运行参数
    包括运行作业1，还是作业2，以及对应的处理方法和配置参数
    """
    runtime = parser.add_argument_group("Environment")
    runtime.add_argument('--work-task', type=str, default='Drama',
                         help='Drama is work1, Trec is work2')

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
