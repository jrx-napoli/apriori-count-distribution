from ucimlrepo import fetch_ucirepo

def dummy():
    return [
        ["1", "3", "4"],
        ["2", "3", "5"],
        ["1", "2", "3", "5"],
        ["2", "5"],
        ["1", "3", "5"]
    ]

def online_retail():
    # fetch dataset
    print("= Online Retail Store =")
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
