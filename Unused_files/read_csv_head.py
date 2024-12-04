import pandas as pd

# Read just the first few rows of the CSV file
df = pd.read_csv('C:/GCI_Hackathon/Location Data/Dummy - Patient Location.csv')
print("\nColumns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
