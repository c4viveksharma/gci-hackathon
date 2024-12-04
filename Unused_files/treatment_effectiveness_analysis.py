import pandas as pd
import matplotlib.pyplot as plt

def load_data(year):
    # Load the datasets for a specific year
    treated = pd.read_csv(f'Treatment Data/Treated_Cases_{year}.csv')
    expected = pd.read_csv(f'Treatment Data/Expected_Cases_{year}.csv')
    return treated, expected

def analyze_treatment_coverage(treated_df, expected_df, year):
    print(f"\n=== Treatment Coverage Analysis for {year} ===")
    
    # Merge treated and expected cases
    merged_df = pd.merge(treated_df, expected_df, on='Country Name', suffixes=('_treated', '_expected'))
    
    # Calculate coverage rate
    merged_df['coverage_rate'] = (merged_df['Total new children treated'] / 
                                merged_df['Expected number of clubfoot cases'] * 100)
    
    print(f"\nOverall Treatment Coverage Statistics for {year}:")
    print("\nCoverage Rate Statistics (%):")
    print(merged_df['coverage_rate'].describe())
    
    # Top 5 countries by coverage
    print("\nTop 5 Countries by Coverage Rate:")
    top_coverage = merged_df.nlargest(5, 'coverage_rate')[
        ['Country Name', 'coverage_rate', 'Total new children treated', 'Expected number of clubfoot cases']]
    print(top_coverage)
    
    return merged_df

def analyze_age_distribution(treated_df, year):
    print(f"\n=== Age Distribution Analysis for {year} ===")
    
    age_columns = ['0-1 years', '1-2 years', '2-3 years', '3-4 years', 
                  '4-5 years', '5-10 years', '10-15 years', '15+ years']
    
    # Calculate total cases by age group
    age_totals = treated_df[age_columns].sum()
    total_cases = age_totals.sum()
    
    # Calculate percentages
    age_percentages = (age_totals / total_cases * 100).round(1)
    
    print("\nAge Distribution of Cases:")
    for age_group, percentage in age_percentages.items():
        print(f"{age_group}: {percentage}%")
    
    # Plot age distribution
    plt.figure(figsize=(12, 6))
    age_percentages.plot(kind='bar')
    plt.title(f'Age Distribution of Treatment Cases - {year}')
    plt.xlabel('Age Group')
    plt.ylabel('Percentage of Cases')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'age_distribution_{year}.png')
    plt.close()

def analyze_treatment_completion(treated_df, year):
    print(f"\n=== Treatment Completion Analysis for {year} ===")
    
    # Calculate completion rates where data is available
    mask = (treated_df['number children started 1yr FAB'].notna() & 
            treated_df['number of children completed 2 years FAB'].notna() &
            treated_df['number children started 1yr FAB'] > 0)
    
    if mask.any():
        completion_df = treated_df[mask].copy()
        completion_df['completion_rate'] = (completion_df['number of children completed 2 years FAB'] / 
                                         completion_df['number children started 1yr FAB'] * 100)
        
        print("\nTreatment Completion Statistics:")
        print("\nNumber of countries with completion data:", len(completion_df))
        print("\nCompletion Rate Statistics (%):")
        print(completion_df['completion_rate'].describe())
        
        # Top 5 countries by completion rate
        print("\nTop 5 Countries by Completion Rate:")
        top_completion = completion_df.nlargest(5, 'completion_rate')[
            ['Country Name', 'completion_rate', 'number children started 1yr FAB', 'number of children completed 2 years FAB']]
        print(top_completion)

def analyze_regional_patterns(treated_df, expected_df, year):
    print(f"\n=== Regional Analysis for {year} ===")
    
    # Merge datasets
    merged_df = pd.merge(treated_df, expected_df, on=['Country Name', 'WHO Region'], suffixes=('_treated', '_expected'))
    
    # Regional statistics
    regional_stats = merged_df.groupby('WHO Region').agg({
        'Total new children treated': 'sum',
        'Expected number of clubfoot cases': 'sum'
    }).round(2)
    
    regional_stats['coverage_rate'] = (regional_stats['Total new children treated'] / 
                                     regional_stats['Expected number of clubfoot cases'] * 100).round(2)
    
    print("\nRegional Coverage Statistics:")
    print(regional_stats.sort_values('coverage_rate', ascending=False))
    
    # Plot regional coverage
    plt.figure(figsize=(12, 6))
    regional_stats['coverage_rate'].plot(kind='bar')
    plt.title(f'Regional Treatment Coverage Rates - {year}')
    plt.xlabel('Region')
    plt.ylabel('Coverage Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'regional_coverage_{year}.png')
    plt.close()

def main():
    years = [2019, 2021, 2023]
    
    for year in years:
        try:
            print(f"\n{'='*20} Analysis for Year {year} {'='*20}")
            treated_df, expected_df = load_data(year)
            
            # Perform analyses
            merged_df = analyze_treatment_coverage(treated_df, expected_df, year)
            analyze_age_distribution(treated_df, year)
            analyze_treatment_completion(treated_df, year)
            analyze_regional_patterns(treated_df, expected_df, year)
            
        except Exception as e:
            print(f"Error analyzing year {year}: {str(e)}")
    
    print("\nAnalysis completed successfully!")
    print("Visualizations have been saved as PNG files.")

if __name__ == "__main__":
    main()
