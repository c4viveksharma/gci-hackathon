import pandas as pd
import matplotlib.pyplot as plt
import textwrap

# Read the survey data
df = pd.read_csv('Survey Data/Cleaned Survey Data.csv')

def basic_statistics(df):
    # Get summary statistics for numerical columns
    print("\n=== Basic Statistics ===")
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    print(df[numeric_columns].describe())
    
    # Count of responses by country
    print("\n=== Response Count by Country ===")
    country_col = df.columns[1]  # Second column contains country data
    country_counts = df[country_col].value_counts()
    print(f"\nTotal number of countries: {len(country_counts)}")
    print("\nTop 10 countries by number of responses:")
    print(country_counts.head(10))

def analyze_treatment_coordination(df):
    # Analyze treatment coordination networks
    print("\n=== Treatment Coordination Analysis ===")
    coord_col = df.columns[2]  # Third column contains coordination data
    coordination_counts = df[coord_col].value_counts()
    print("\nTreatment Coordination Distribution:")
    print(coordination_counts)
    
    # Create a pie chart with better formatting
    plt.figure(figsize=(15, 10))
    plt.pie(coordination_counts.values, 
            labels=[textwrap.fill(label, 30) for label in coordination_counts.index], 
            autopct='%1.1f%%')
    plt.title('Distribution of Treatment Coordination Approaches')
    plt.axis('equal')
    plt.savefig('treatment_coordination_pie.png', bbox_inches='tight')
    plt.close()

def analyze_organization_distribution(df):
    # Analyze organizations providing treatment
    print("\n=== Organization Distribution ===")
    org_col = df.columns[0]  # First column contains organization data
    org_counts = df[org_col].value_counts()
    print("\nTop 10 Organizations providing treatment:")
    print(org_counts.head(10))

def analyze_success_rates(df):
    # Extract and analyze success rates
    print("\n=== Success Rates Analysis ===")
    
    # Convert percentage ranges to numeric values (taking the midpoint)
    def extract_midpoint(range_str):
        if pd.isna(range_str):
            return None
        if isinstance(range_str, (int, float)):
            return float(range_str)
        if '-' in range_str:
            low, high = map(lambda x: float(x.strip('%')), range_str.split('-'))
            return (low + high) / 2
        return None

    # Analyze success rates if the columns exist
    success_rate_columns = [col for col in df.columns if 'success' in col.lower()]
    if success_rate_columns:
        for col in success_rate_columns:
            df[f'{col}_numeric'] = df[col].apply(extract_midpoint)
            print(f"\nStatistics for {col}:")
            print(df[f'{col}_numeric'].describe())

def main():
    try:
        # Execute analysis functions
        basic_statistics(df)
        analyze_treatment_coordination(df)
        analyze_organization_distribution(df)
        analyze_success_rates(df)
        
        print("\nAnalysis completed successfully!")
        print("A pie chart has been saved as 'treatment_coordination_pie.png'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
