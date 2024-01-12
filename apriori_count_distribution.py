from multiprocessing import Process, Manager
from itertools import combinations

def count_itemsets_local(data_chunk, candidate_itemsets, local_count_dist):
    """Count local support for candidate itemsets in a data chunk

    Args:
        data_chunk (_type_): _description_
        candidate_itemsets (_type_): _description_
        local_count_dist (_type_): _description_
    """
    local_support = {}

    for transaction in data_chunk:
        for itemset in candidate_itemsets:
            if set(itemset).issubset(transaction):
                local_support.setdefault(tuple(itemset), 0)
                local_support[tuple(itemset)] += 1

    # Update the local count distribution
    for itemset, support in local_support.items():
        local_count_dist[itemset] += support

def parallel_count_distribution_apriori(data, min_support, num_processes):
    """_summary_

    Args:
        data (_type_): _description_
        min_support (_type_): _description_
        num_processes (_type_): _description_
    """
    # Initialize global count distribution using a shared manager
    with Manager() as manager:
        global_count_dist = manager.dict()

        # Initialize the dataset partitioning
        chunk_size = len(data) // num_processes
        data_chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        # Perform initial pass to get 1-itemset support
        candidate_1_itemsets = [set(item) for item in set(item for transaction in data for item in transaction)]
        local_count_dist = manager.dict({itemset: 0 for itemset in map(tuple, candidate_1_itemsets)})

        processes = []

        # Parallel processing for initial count distribution
        for i in range(num_processes):
            p = Process(target=count_itemsets_local, args=(data_chunks[i], candidate_1_itemsets, local_count_dist))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        # TODO: is this redundant? is global support == local support in this case?
        # Aggregate local count distributions to obtain global count distribution
        for itemset, support in local_count_dist.items():
            global_count_dist[itemset] = support

        # Prune infrequent itemsets based on global count distribution
        frequent_itemsets = [list(itemset) for itemset, support in global_count_dist.items() if support >= min_support]
        
        # Display frequent itemsets for first iteration
        print(f"Frequent Itemsets (Iteration 1): {frequent_itemsets}")

        iteration = 2
        
        while True:
            # Generate candidate itemsets for the current iteration
            candidate_itemsets = generate_candidate_itemsets(frequent_itemsets, iteration)

            # Check if there are any candidate itemsets
            if not candidate_itemsets:
                break

            # Initialize local count distribution for the current iteration
            local_count_dist = manager.dict({itemset: 0 for itemset in map(tuple, candidate_itemsets)})

            processes = []

            # Parallel processing for counting support of candidate itemsets
            for i in range(num_processes):
                p = Process(target=count_itemsets_local, args=(data_chunks[i], candidate_itemsets, local_count_dist))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()

            # Aggregate local count distributions to obtain global count distribution
            for itemset, support in local_count_dist.items():
                global_count_dist[itemset] = support

            # Prune infrequent itemsets based on global count distribution
            frequent_itemsets = [list(itemset) for itemset, support in global_count_dist.items() if support >= min_support]

            # Display or store frequent itemsets for the current iteration
            print(f"Frequent Itemsets (Iteration {iteration}): {frequent_itemsets}")

            iteration += 1

def generate_candidate_itemsets(frequent_itemsets, k):
    """
    Generate candidate k-itemsets from frequent (k-1)-itemsets.

    Parameters:
    - frequent_itemsets: List of frequent (k-1)-itemsets from the previous iteration.
    - k: Size of the itemsets to generate (k-itemsets).

    Returns:
    - candidate_itemsets: List of candidate k-itemsets.
    """
    candidate_itemsets = []

    # Generate candidate itemsets by joining (k-1)-itemsets
    for i in range(len(frequent_itemsets)):
        for j in range(i + 1, len(frequent_itemsets)):
            itemset1 = frequent_itemsets[i]
            itemset2 = frequent_itemsets[j]

            # Join the itemsets if the first (k-2) elements are the same
            if itemset1[:k-2] == itemset2[:k-2]:
                # Create a new candidate by joining the last elements
                new_itemset = sorted(set(itemset1).union(itemset2))

                # Prune the candidate if it has an infrequent subset
                if not has_infrequent_subset(new_itemset, frequent_itemsets, k-1):
                    candidate_itemsets.append(new_itemset)

    return candidate_itemsets

def has_infrequent_subset(itemset, frequent_itemsets, k):
    """
    Check if a candidate itemset has an infrequent subset.

    Parameters:
    - itemset: Candidate itemset.
    - frequent_itemsets: List of frequent (k-1)-itemsets.
    - k: Size of the subset to check.

    Returns:
    - True if the candidate has an infrequent subset, False otherwise.
    """
    # Generate all possible subsets of size k from the candidate itemset
    subsets = list(combinations(itemset, k))

    # Check if any subset is not frequent
    for subset in subsets:
        if list(subset) not in frequent_itemsets:
            return True  # Candidate has an infrequent subset

    return False  # Candidate does not have an infrequent subset

# Example usage
if __name__ == "__main__":
    # Example dataset
    dataset = [
        ["1", "3", "4"],
        ["2", "3", "5"],
        ["1", "2", "3", "5"],
        ["2", "5"],
        ["1", "3", "5"]

        # ["a", "b"],
        # ["a", "c", "d"],
        # ["b", "c", "d", "e"]
        # ... more transactions
    ]

    # Minimum support threshold
    min_support = 2

    # Number of processes
    num_processes = 1

    # Run the parallel count distribution Apriori algorithm
    parallel_count_distribution_apriori(dataset, min_support, num_processes)
