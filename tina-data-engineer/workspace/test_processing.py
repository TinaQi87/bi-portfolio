#!/usr/bin/env python3
"""
Simple Data Processing Script
Tests pandas and basic data operations
"""

import pandas as pd
import sys

def main():
    print("=" * 50)
    print("Data Processing Test Script")
    print("=" * 50)
    
    # Test 1: Load CSV
    print("\n1. Loading CSV file...")
    try:
        df = pd.read_csv('sample_data.csv')
        print(f"✅ CSV loaded successfully! Shape: {df.shape}")
        print(f"\nFirst 3 rows:")
        print(df.head(3))
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return
    
    # Test 2: Basic Statistics
    print("\n2. Calculating statistics...")
    print(f"\nAverage Salary: ${df['salary'].mean():,.2f}")
    print(f"Max Salary: ${df['salary'].max():,.2f}")
    print(f"Min Salary: ${df['salary'].min():,.2f}")
    
    # Test 3: Group By
    print("\n3. Grouping by city...")
    city_stats = df.groupby('city')['salary'].agg(['mean', 'count'])
    print(city_stats)
    
    # Test 4: Filter Data
    print("\n4. Filtering high earners (>$90k)...")
    high_earners = df[df['salary'] > 90000]
    print(f"Found {len(high_earners)} high earners:")
    print(high_earners[['name', 'salary']])
    
    # Test 5: Create new column
    print("\n5. Adding calculated column...")
    df['salary_category'] = df['salary'].apply(
        lambda x: 'High' if x > 90000 else 'Medium' if x > 80000 else 'Standard'
    )
    print(df[['name', 'salary', 'salary_category']])
    
    # Test 6: Export results
    print("\n6. Exporting processed data...")
    output_file = 'processed_data.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Data exported to {output_file}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
