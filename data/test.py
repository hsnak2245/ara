import pandas as pd

# List of parquet files
parquet_files = ['acc.parquet', 'liz.parquet', 'veh.parquet']

for file in parquet_files:
    # Read the parquet file
    df = pd.read_parquet(file)
    
    # Display the head of the dataframe
    print(f"Head of {file}:")
    print(df.head())
    
    # Display the summary of the dataframe
    print(f"Summary of {file}:")
    print(df.describe())
    print("\n" + "="*50 + "\n")
    