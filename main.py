import sys
import dataset_generation
from options import get_args
from apriori_count_distribution import find_frequent_itemsets, generate_association_rules


if __name__ == '__main__':
    args = get_args(sys.argv[1:])
    data = dataset_generation.__dict__[args.dataset]()
    
    frequent_itemsets = find_frequent_itemsets(data=data, num_processes=args.num_processes, min_support=args.min_support)
    association_rules = generate_association_rules(frequent_itemsets=frequent_itemsets, num_processes=args.num_processes, min_confidence=args.min_confidence)
