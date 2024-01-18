# Parallel Mining of Association Rules
Implementation of Count Distribution modification to the Apriori algorithm introduced in [Parallel Mining of Association Rules](https://ieeexplore.ieee.org/document/553164).

#### Run:
```
python main.py --dataset online_retail --num_processes 8 --min_support 200 --min_confidence 0.7
```

#### Available options
`--dataset_path` path to local dataset file

`--dataset` (overritten by `--dataset_path`) name of a pre-created dataset available in this package

`--num_processes` number of parallel workers

`--min_support` minimal itemset support

`--min_confidence` minimal confidence