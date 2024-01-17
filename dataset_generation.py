from ucimlrepo import fetch_ucirepo
import pandas as pd

def read_dataset(path):
    print(f"Dataset path: {path}")
    print("Reading dataset...")
    df = pd.read_csv(path, delimiter=";")
    
    # Create a matrix of transactions
    print("Transforming...")
    dataset = df.groupby('Invoice')['StockCode'].apply(list).reset_index(name='StockCodes')
    dataset = dataset['StockCodes'].tolist()

    return dataset

def online_retail():
    # fetch dataset
    print("= Online Retail =")
    print("Downloading dataset...")
    raw_data = fetch_ucirepo(id=352) 
    df = raw_data.data.original

    # Create a matrix of transactions
    print("Transforming...")
    basket = (df.groupby(['InvoiceNo', 'StockCode'])['StockCode']
              .count()
              .unstack()
              .reset_index()
              .fillna(0)
              .set_index('InvoiceNo'))

    # Convert counts to binary values (1 if item was bought in the transaction, 0 otherwise)
    basket_sets = basket.applymap(lambda x: 1 if x > 0 else 0)

    # Convert matrix to a list of transactions
    transformed_dataset = basket_sets.apply(lambda row: row.index[row.astype(bool)].tolist(), axis=1).tolist()
    return transformed_dataset

def online_retail_ii():
    print("= Online Retail II =")
    print("Downloading dataset...")
    df = pd.read_csv("dataset/online_retail_ii.csv", delimiter=";")
    
    # Create a matrix of transactions
    print("Transforming...")
    basket = (df.groupby(['Invoice', 'StockCode'])['StockCode']
              .count()
              .unstack()
              .reset_index()
              .fillna(0)
              .set_index('Invoice'))

    # Convert counts to binary values (1 if item was bought in the transaction, 0 otherwise)
    basket_sets = basket.applymap(lambda x: 1 if x > 0 else 0)

    # Convert matrix to a list of transactions
    transformed_dataset = basket_sets.apply(lambda row: row.index[row.astype(bool)].tolist(), axis=1).tolist()
    return transformed_dataset
