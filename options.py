import argparse

def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_processes', default=1, type=int, help="Number of processors used for count distribution")
    parser.add_argument('--min_support', default=2, type=int, help="Minimal support")
    parser.add_argument('--dataset', default="online_retail", type=str, help="Dataset name")

    return parser.parse_args(argv)
