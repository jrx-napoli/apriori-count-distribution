from multiprocessing import Process, Manager, Lock
import random
import time

def count_initial_itemsets_local(data_chunk, local_count_dist, lock):
    """
    Counts local support for candidate itemsets in a data chunk
    during the first iteration. Count is done for unique, k=1 candidate itemsets
    available in a provided data partition.

    Args:
        data_chunk (list): Data partition containing a list of transactions
        local_count_dist (dict): Dictionary keeping a record of local support counts
    
    Returns:
        void
    """
    initial_candidate_itemsets = [[item] for item in set(item for transaction in data_chunk for item in transaction)]
    count_itemsets_local(data_chunk, initial_candidate_itemsets, local_count_dist, lock)

def count_itemsets_local(data_chunk, candidate_itemsets, local_count_dist, lock):
    """
    Counts local support for candidate itemsets in a data chunk.

    Args:
        data_chunk (list): Data partition containing a list of transactions
        candidate_itemsets (list): List of candidate itemsets
        local_count_dist (dist): Dictionary keeping a record of local support counts

    Returns:
        void
    """
    local_support = {}

    for transaction in data_chunk:
        for itemset in candidate_itemsets:
            if set(itemset).issubset(transaction):
                local_support.setdefault(tuple(itemset), 0)
                local_support[tuple(itemset)] += 1

    # Update the local count distribution
    with lock:
        for itemset, support in local_support.items():
            local_count_dist[itemset] += support

def generate_candidate_itemsets(frequent_itemsets, k):
    """
    Generates candidate k-itemsets from frequent (k-1)-itemsets.

    Args:
        frequent_itemsets (list): List of frequent (k-1)-itemsets from the previous iteration.
        k (int): Size of the itemsets to generate (k-itemsets).

    Returns:
        candidate_itemsets (list): List of candidate k-itemsets.
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

                # Prune the candidate if it has an infrequent subset - apriori rule
                if not has_infrequent_subset(new_itemset, frequent_itemsets, k-1):
                    candidate_itemsets.append(new_itemset)

    return candidate_itemsets

def has_infrequent_subset(itemset, frequent_itemsets, k):
    """
    Checks if a candidate itemset has an infrequent subset.

    Args:
        itemset (list): Candidate itemset.
        frequent_itemsets (list): List of frequent (k-1)-itemsets.
        k (int): Size of the subset to check.

    Returns:
        (boolean): True if the candidate has an infrequent subset, False otherwise.
    """
    # Generate all possible subsets of size k from the candidate itemset
    subsets = list(generate_combinations(itemset, k))

    # Check if any subset is not frequent
    for subset in subsets:
        if list(subset) not in frequent_itemsets:
            return True

    return False  # Candidate does not have an infrequent subset

def generate_combinations(items, k):
    """
    Generate all combinations of length k from a list of items.
    
    Args:
        itemset (list): List of items.
        k (int): Length of combinations to generate.
    
    Returns:
        (list): List of combinations.
    """
    if k == 0:
        return [()]
    if not items:
        return []

    first_item = items[0]
    rest_items = items[1:]

    # Recursively generate combinations including the first item and excluding the first item
    with_first_item = [(first_item,) + combo for combo in generate_combinations(rest_items, k - 1)]
    without_first_item = generate_combinations(rest_items, k)

    return with_first_item + without_first_item

def find_frequent_itemsets(data, num_processes, min_support):
    """
    Implements the Apriori algorithm with parallel count distribution.

    Args:
        data (list): Dataset
        min_support (int): Minimal support of a frequent itemset
        num_processes (int): Number of processes to perform parallel computations

    Returns:
        frequent_itemsets (list): List of frequent itemsets 
        global_count_dist (dict): Global count distribution of all frequent itemsets
    """
    print("\nDiscovering frequent itemsets:")
    # Initialize global count distribution using a shared manager
    with Manager() as manager:
        global_count_dist = manager.dict()

        # Verify that there is enough data to distribute
        if num_processes > len(data): num_processes = len(data)

        # Initialize the dataset partitioning
        chunk_size = len(data) // num_processes
        remaining_data = len(data) % num_processes

        data_chunks = [data[i * chunk_size:(i + 1) * chunk_size] for i in range(num_processes)]
        data_chunks[-1].extend(data[num_processes * chunk_size:num_processes * chunk_size + remaining_data])

        # Perform initial pass to get 1-itemset support
        # NOTE: In theory, in the first pass, each processor is supposed to generate 
        # a unique, local candidate itemsets depending on its particular partition.
        # These itemsets should only be synchronised at a later step.
        initial_candidate_itemsets = [[item] for item in set(item for transaction in data for item in transaction)]
        local_count_dist = manager.dict({itemset: 0 for itemset in map(tuple, initial_candidate_itemsets)})

        lock = Lock()
        processes = []
        time_start = time.time()

        # Parallel processing for initial count distribution
        for i in range(num_processes):
            p = Process(target=count_initial_itemsets_local, args=(data_chunks[i], local_count_dist, lock))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        # Aggregate local count distributions to obtain global count distribution
        for itemset, support in local_count_dist.items():
            global_count_dist[itemset] = support

        # Prune infrequent itemsets based on global count distribution
        frequent_itemsets = [list(itemset) for itemset, support in global_count_dist.items() if support >= min_support]
        
        # Display frequent itemsets for first iteration
        print(f"Iteration 1 [{round(time.time() - time_start, 2)} s]: {len(frequent_itemsets)} total")

        iteration = 2
        
        while True:
            time_start = time.time()

            # Generate candidate itemsets for the current iteration
            candidate_itemsets = generate_candidate_itemsets(frequent_itemsets, iteration)

            # End computing if there are no candidate itemsets
            if not candidate_itemsets:
                break

            # Initialize local count distribution for the current iteration
            local_count_dist = manager.dict({itemset: 0 for itemset in map(tuple, candidate_itemsets)})

            processes = []

            # Parallel processing for counting support of candidate itemsets
            for i in range(num_processes):
                p = Process(target=count_itemsets_local, args=(data_chunks[i], candidate_itemsets, local_count_dist, lock))
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
            print(f"Iteration {iteration} [{round(time.time() - time_start, 2)} s]: {len(frequent_itemsets)} total")

            iteration += 1
        
        return frequent_itemsets, dict(global_count_dist)

def generate_association_rules(frequent_itemsets, global_count_dist, num_processes, min_confidence):
    """
    Generates association rules for provided frequent itemsets.

    Args:
        frequent_itemsets (list): List of frequent itemsets 
        global_count_dist (dict): Global count distribution of all frequent itemsets
        num_processes (int): Number of processes to perform parallel computations
        min_confidence (float): Minimal confidence to support a rule

    Returns:
        (list): List of generated association rules
    """
    print("\nGenerating association rules:")
    with Manager() as manager:
        association_rules = manager.list()

        lock = Lock()
        processes = []

        # Partition frequent itemsets by length and distribute among processors
        # NOTE: Since the number of rules that can be generated from an
        # itemset is sensitive to the itemset's size, we attempt equitable balancing 
        # by partitioning the itemsets of each length equally across the processors.
        itemsets_by_length = {}
        for itemset in frequent_itemsets:
            length = len(itemset)
            itemsets_by_length.setdefault(length, []).append(itemset)

        time_start = time.time()

        for length, itemsets in itemsets_by_length.items():
            chunk_size = len(itemsets) // num_processes
            remaining_itemsets = len(itemsets) % num_processes

            itemset_chunks = [itemsets[i * chunk_size:(i + 1) * chunk_size] for i in range(num_processes)]
            itemset_chunks[-1].extend(itemsets[num_processes * chunk_size:num_processes * chunk_size + remaining_itemsets])

            # Parallel processing for generating association rules
            for i in range(num_processes):
                p = Process(target=generate_rules_local, args=(itemset_chunks[i], global_count_dist, min_confidence, association_rules, lock))
                processes.append(p)
                p.start()

        for p in processes:
            p.join()

        # Convert manager.list to a regular list for easier handling
        association_rules = list(association_rules)
        print(f"Generated {len(association_rules)} rules [{round(time.time() - time_start, 2)} s]")
        print(association_rules)

        return association_rules

def generate_rules_local(itemset_chunk, global_count_dist, min_confidence, association_rules, lock):
    """
    Generates association rules for a local itemset partition.

    Args:
        itemset_chunk (list): Partition of frequent itemsets
        global_count_dist (dict): Global count distribution of all frequent itemsets
        min_confidence (float): Minimal confidence to support a rule
        association_rules (list): List of association rules shared between processes
        lock (Lock): Lock guarding shared list of rules
    
    Returns:
        void
    """
    # local_rules = []

    # for itemset in itemset_chunk:
    #     if len(itemset) > 1:
    #         for i in range(1, len(itemset)):
    #             antecedent = itemset[:i]
    #             consequent = itemset[i:]

    #             support_itemset = global_count_dist[tuple(itemset)]
    #             support_antecedent = global_count_dist[tuple(antecedent)]
    #             confidence = support_itemset / support_antecedent

    #             if confidence >= min_confidence:
    #                 local_rules.append((antecedent, consequent, round(confidence, 3)))

    # with lock:
    #     association_rules.extend(local_rules)

    local_rules = []

    # Iterate over all itemsets in data partition 
    for itemset in itemset_chunk:
        if len(itemset) > 1:

            # Begin examining largest subsets as antecedents first
            antecedent_max_len = len(itemset) - 1
            for antecedent_len in range(antecedent_max_len, 0, -1):

                found_rule = False
                # Iterate over all possible antecedent of selected size
                all_antecedents = generate_combinations(itemset, antecedent_len)
                for antecedent in all_antecedents:

                    # Calculate rule confidence
                    consequent = itemset - antecedent
                    support_itemset = global_count_dist[tuple(itemset)]
                    support_antecedent = global_count_dist[tuple(antecedent)]
                    confidence = support_itemset / support_antecedent

                    # Store rule meeting confidence threshold
                    if confidence >= min_confidence:
                        local_rules.append((antecedent, consequent, round(confidence, 3)))
                        found_rule = True
                
                # If no rule was established for given antecedent size,
                # discard all smaller antecedents as well
                if not found_rule:
                    break

    with lock:
        association_rules.extend(local_rules)
