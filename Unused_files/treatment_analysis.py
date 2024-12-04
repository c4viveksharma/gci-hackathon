import pandas as pd
import matplotlib.pyplot as plt

# Read the treatment data
df = pd.read_csv('Treatment Data/Processed_Treatment_Cases_All_Years.csv')

def basic_statistics(df):
    print("\n=== Basic Statistics of Treatment Cases ===")
    print("\nTotal Cases Statistics:")
    print(df['Total new children treated'].describe())
    
    print("\n=== Age Group Distribution ===")
    age_groups = ['0-1 years', '1-2 years', '2-3 years', '3-4 years', 
                 '4-5 years', '5-10 years', '10-15 years', '15+ years']
    age_totals = df[age_groups].sum()
    print("\nTotal cases by age group:")
    print(age_totals)

def analyze_yearly_trends(df):
    print("\n=== Yearly Treatment Analysis ===")
    yearly_cases = df.groupby('YEAR_RECORDED')['Total new children treated'].sum()
    print("\nTotal cases per year:")
    print(yearly_cases)
    
    # Plot yearly trends
    plt.figure(figsize=(12, 6))
    yearly_cases.plot(kind='bar')
    plt.title('Total Number of Treatment Cases by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Cases')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('yearly_treatment_cases.png')
    plt.close()

def analyze_regional_distribution(df):
    print("\n=== Regional Distribution Analysis ===")
    regional_cases = df.groupby('Region')['Total new children treated'].sum().sort_values(ascending=False)
    print("\nTotal cases by region:")
    print(regional_cases)
    
    # Plot regional distribution
    plt.figure(figsize=(12, 6))
    regional_cases.plot(kind='bar')
    plt.title('Treatment Cases by Region')
    plt.xlabel('Region')
    plt.ylabel('Number of Cases')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('regional_distribution.png')
    plt.close()

def analyze_income_groups(df):
    print("\n=== Income Group Analysis ===")
    income_cases = df.groupby('Income Group')['Total new children treated'].sum().sort_values(ascending=False)
    print("\nTotal cases by income group:")
    print(income_cases)
    
    # Plot income group distribution
    plt.figure(figsize=(10, 6))
    income_cases.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Distribution of Cases by Income Group')
    plt.axis('equal')
    plt.savefig('income_group_distribution.png')
    plt.close()

def analyze_treatment_completion(df):
    print("\n=== Treatment Completion Analysis ===")
    print("\nFAB Treatment Statistics:")
    print("\nChildren who started 1-year FAB:")
    print(df['number children started 1yr FAB'].describe())
    print("\nChildren who completed 2 years FAB:")
    print(df['number of children completed 2 years FAB'].describe())
    
    # Calculate completion rate where data is available
    mask = (df['number children started 1yr FAB'] > 0) & (df['number of children completed 2 years FAB'] > 0)
    if mask.any():
        completion_rate = (df[mask]['number of children completed 2 years FAB'] / 
                         df[mask]['number children started 1yr FAB'] * 100)
        print("\nCompletion Rate Statistics (where data available):")
        print(completion_rate.describe())

def main():
    try:
        # Execute analysis functions
        basic_statistics(df)
        analyze_yearly_trends(df)
        analyze_regional_distribution(df)
        analyze_income_groups(df)
        analyze_treatment_completion(df)
        
        print("\nAnalysis completed successfully!")
        print("Visualizations have been saved as PNG files.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
