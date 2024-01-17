import sys
import dataset_generation
import utils
from options import get_args
from apriori_count_distribution import find_frequent_itemsets, generate_association_rules


def run(args):

    if args.dataset_path is not None:
        data = dataset_generation.read_dataset(args.dataset_path)
    else:
        data = dataset_generation.__dict__[args.dataset]()
        
    frequent_itemsets, global_count_dist = find_frequent_itemsets(data=data, 
                                                                  num_processes=args.num_processes, 
                                                                  min_support=args.min_support)
    association_rules = generate_association_rules(frequent_itemsets=frequent_itemsets, 
                                                   global_count_dist=global_count_dist,
                                                   num_processes=args.num_processes, 
                                                   min_confidence=args.min_confidence)
    utils.save_to_file(association_rules)

if __name__ == '__main__':
    args = get_args(sys.argv[1:])
    run(args)
    