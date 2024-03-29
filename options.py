import argparse

def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_path', default=None, type=str, help="Dataset path")
    parser.add_argument('--dataset', default=None, type=str, help="Predefined dataset name")
    parser.add_argument('--num_processes', default=1, type=int, help="Number of processors used for count distribution")
    parser.add_argument('--min_support', default=2, type=int, help="Minimal support")
    parser.add_argument('--min_confidence', default=0.7, type=float, help="Minimal confidence")

    return parser.parse_args(argv)
