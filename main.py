import sys
import dataset_gen
from options import get_args
from apriori_count_distribution import find_frequent_itemsets


if __name__ == '__main__':
    args = get_args(sys.argv[1:])
    data = dataset_gen.__dict__[args.dataset]()
    find_frequent_itemsets(data=data, num_processes=args.num_processes, min_support=args.min_support)
