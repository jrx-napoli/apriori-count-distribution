import sys
from options import get_args
from apriori_count_distribution import find_frequent_itemsets
from dataset_gen import get_data

if __name__ == '__main__':
    args = get_args(sys.argv[1:])
    data = get_data()

    find_frequent_itemsets(data=data, num_processes=args.num_processes, min_support=args.min_support)
