#!/usr/bin/env python3
"""
Google Play Store Data Analysis, Cleaning, SQL & Visualization Project
=====================================================================
This script performs:
  1. Data Loading & Profiling
  2. Data Cleaning (missing values, duplicates, data types, outliers)
  3. SQLite Database creation & SQL queries
  4. Visualizations (matplotlib / seaborn)
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 5)

# ============================================================
# 1. DATA LOADING & PROFILING
# ============================================================
print("=" * 70)
print("1. DATA LOADING & PROFILING")
print("=" * 70)

# Load main dataset
df = pd.read_csv('googleplaystore.csv')
print(f"\nDataset shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")

print("\n--- df.info() ---")
df.info()

print("\n--- df.describe() ---")
print(df.describe(include='all'))

print("\n--- Missing Values per Column ---")
missing = df.isnull().sum()
print(missing[missing > 0])

print("\n--- Data Types ---")
print(df.dtypes)

# Identify columns with incorrect data types (numbers stored as strings)
print("\n--- Potential Data Type Issues ---")
# Reviews should be numeric
print(f"  Reviews sample: {df['Reviews'].head(5).tolist()}")
# Size has M/k suffixes
print(f"  Size sample: {df['Size'].head(5).tolist()}")
# Installs has commas and +
print(f"  Installs sample: {df['Installs'].head(5).tolist()}")
# Price has $ symbol
print(f"  Price sample: {df['Price'].head(5).tolist()}")

# ============================================================
# 2. DATA CLEANING
# ============================================================
print("\n" + "=" * 70)
print("2. DATA CLEANING")
print("=" * 70)

df_clean = df.copy()

# --- 2a. Handle Missing Values ---
print("\n--- Handling Missing Values ---")
missing_pct = (df_clean.isnull().sum() / len(df_clean)) * 100
print(f"Missing % per column:\n{missing_pct[missing_pct > 0]}")

# Drop columns with >10% missing values
cols_to_drop = missing_pct[missing_pct > 10].index.tolist()
if cols_to_drop:
    print(f"\nDropping columns with >10% missing: {cols_to_drop}")
    df_clean.drop(columns=cols_to_drop, inplace=True)
else:
    print("\nNo columns with >10% missing values to drop.")

# Handle remaining missing values
# Rating: ~13.6% missing - that's >10%, so drop column
# Actually Rating has 1474/10841 = 13.59% missing, so drop it
if 'Rating' in df_clean.columns:
    print("Rating has 13.6% missing (>10%) -> dropping column")
    df_clean.drop(columns=['Rating'], inplace=True)

# Type: 1 missing -> impute with mode
if 'Type' in df_clean.columns and df_clean['Type'].isnull().sum() > 0:
    type_mode = df_clean['Type'].mode()[0]
    print(f"Type missing: {df_clean['Type'].isnull().sum()} -> imputing with mode '{type_mode}'")
    df_clean['Type'].fillna(type_mode, inplace=True)

# Content Rating: 1 missing -> impute with mode
if 'Content Rating' in df_clean.columns and df_clean['Content Rating'].isnull().sum() > 0:
    cr_mode = df_clean['Content Rating'].mode()[0]
    print(f"Content Rating missing: {df_clean['Content Rating'].isnull().sum()} -> imputing with mode '{cr_mode}'")
    df_clean['Content Rating'].fillna(cr_mode, inplace=True)

# Current Ver: 8 missing -> impute with mode
if 'Current Ver' in df_clean.columns and df_clean['Current Ver'].isnull().sum() > 0:
    cv_mode = df_clean['Current Ver'].mode()[0]
    print(f"Current Ver missing: {df_clean['Current Ver'].isnull().sum()} -> imputing with mode '{cv_mode}'")
    df_clean['Current Ver'].fillna(cv_mode, inplace=True)

# Android Ver: 3 missing -> impute with mode
if 'Android Ver' in df_clean.columns and df_clean['Android Ver'].isnull().sum() > 0:
    av_mode = df_clean['Android Ver'].mode()[0]
    print(f"Android Ver missing: {df_clean['Android Ver'].isnull().sum()} -> imputing with mode '{av_mode}'")
    df_clean['Android Ver'].fillna(av_mode, inplace=True)

print(f"\nMissing values after cleaning:\n{df_clean.isnull().sum()[df_clean.isnull().sum() > 0]}")

# --- 2b. Remove Duplicate Rows ---
print("\n--- Removing Duplicates ---")
dup_count = df_clean.duplicated().sum()
print(f"Duplicate rows found: {dup_count}")
df_clean.drop_duplicates(inplace=True)
print(f"Shape after removing duplicates: {df_clean.shape}")

# --- 2c. Clean Data Types ---
print("\n--- Cleaning Data Types ---")

# Reviews: convert to int
df_clean['Reviews'] = df_clean['Reviews'].astype(str).str.replace(',', '').str.strip()
df_clean['Reviews'] = pd.to_numeric(df_clean['Reviews'], errors='coerce').fillna(0).astype(int)
print("  Reviews -> int")

# Size: convert to numeric (MB)
def clean_size(size_str):
    if pd.isna(size_str):
        return np.nan
    size_str = str(size_str).strip()
    if size_str == 'Varies with device':
        return np.nan
    if 'M' in size_str:
        return float(size_str.replace('M', '').strip())
    if 'k' in size_str:
        return float(size_str.replace('k', '').strip()) / 1024
    return np.nan

df_clean['Size_MB'] = df_clean['Size'].apply(clean_size)
print("  Size -> Size_MB (float in MB)")

# Installs: remove commas and +, convert to int
df_clean['Installs'] = df_clean['Installs'].astype(str).str.replace(',', '').str.replace('+', '').str.strip()
df_clean['Installs'] = pd.to_numeric(df_clean['Installs'], errors='coerce').fillna(0).astype(int)
print("  Installs -> int")

# Price: remove $, convert to float
df_clean['Price'] = df_clean['Price'].astype(str).str.replace('$', '').str.strip()
df_clean['Price'] = pd.to_numeric(df_clean['Price'], errors='coerce').fillna(0.0)
print("  Price -> float")

# Type: clean stray values
df_clean['Type'] = df_clean['Type'].astype(str).str.strip()
df_clean.loc[~df_clean['Type'].isin(['Free', 'Paid']), 'Type'] = 'Free'
print("  Type -> cleaned (Free/Paid)")

print(f"\nUpdated dtypes:\n{df_clean.dtypes}")

# --- 2d. Outlier Detection & Treatment (IQR method) ---
print("\n--- Outlier Detection & Treatment (IQR) ---")

# Outlier detection on Reviews
Q1_rev = df_clean['Reviews'].quantile(0.25)
Q3_rev = df_clean['Reviews'].quantile(0.75)
IQR_rev = Q3_rev - Q1_rev
lower_rev = Q1_rev - 1.5 * IQR_rev
upper_rev = Q3_rev + 1.5 * IQR_rev
outliers_rev = df_clean[(df_clean['Reviews'] < lower_rev) | (df_clean['Reviews'] > upper_rev)]
print(f"  Reviews - Q1={Q1_rev}, Q3={Q3_rev}, IQR={IQR_rev}")
print(f"  Reviews - Lower bound={lower_rev}, Upper bound={upper_rev}")
print(f"  Reviews - Outliers count: {len(outliers_rev)} ({len(outliers_rev)/len(df_clean)*100:.2f}%)")
# Cap outliers
df_clean['Reviews'] = df_clean['Reviews'].clip(lower=lower_rev, upper=upper_rev)
print(f"  Reviews - Outliers capped.")

# Outlier detection on Installs
Q1_ins = df_clean['Installs'].quantile(0.25)
Q3_ins = df_clean['Installs'].quantile(0.75)
IQR_ins = Q3_ins - Q1_ins
lower_ins = Q1_ins - 1.5 * IQR_ins
upper_ins = Q3_ins + 1.5 * IQR_ins
outliers_ins = df_clean[(df_clean['Installs'] < lower_ins) | (df_clean['Installs'] > upper_ins)]
print(f"  Installs - Q1={Q1_ins}, Q3={Q3_ins}, IQR={IQR_ins}")
print(f"  Installs - Lower bound={lower_ins}, Upper bound={upper_ins}")
print(f"  Installs - Outliers count: {len(outliers_ins)} ({len(outliers_ins)/len(df_clean)*100:.2f}%)")
# Cap outliers
df_clean['Installs'] = df_clean['Installs'].clip(lower=lower_ins, upper=upper_ins)
print(f"  Installs - Outliers capped.")

# Outlier detection on Price (only for paid apps to avoid zero-IQR issue)
paid_prices = df_clean[df_clean['Price'] > 0]['Price']
if len(paid_prices) > 0:
    Q1_pr = paid_prices.quantile(0.25)
    Q3_pr = paid_prices.quantile(0.75)
    IQR_pr = Q3_pr - Q1_pr
    lower_pr = Q1_pr - 1.5 * IQR_pr
    upper_pr = Q3_pr + 1.5 * IQR_pr
    outliers_pr = df_clean[(df_clean['Price'] > 0) & ((df_clean['Price'] < lower_pr) | (df_clean['Price'] > upper_pr))]
    print(f"  Price (paid only) - Q1={Q1_pr}, Q3={Q3_pr}, IQR={IQR_pr}")
    print(f"  Price (paid only) - Lower bound={lower_pr}, Upper bound={upper_pr}")
    print(f"  Price (paid only) - Outliers count: {len(outliers_pr)}")
    # Cap outliers only for paid apps
    mask_paid = df_clean['Price'] > 0
    df_clean.loc[mask_paid, 'Price'] = df_clean.loc[mask_paid, 'Price'].clip(lower=lower_pr, upper=upper_pr)
    print(f"  Price - Outliers capped (paid apps only).")
else:
    print("  No paid apps to detect price outliers.")

print(f"\nFinal cleaned shape: {df_clean.shape}")

# ============================================================
# 3. SQLite DATABASE & SQL QUERIES
# ============================================================
print("\n" + "=" * 70)
print("3. SQLite DATABASE & SQL QUERIES")
print("=" * 70)

# Create SQLite database
db_path = 'googleplaystore.db'
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
df_clean.to_sql('apps', conn, if_exists='replace', index=False)
print(f"\nDatabase '{db_path}' created. Table 'apps' with {len(df_clean)} rows.")

# Also load and clean the user reviews dataset
df_reviews = pd.read_csv('googleplaystore_user_reviews.csv')
df_reviews.drop_duplicates(inplace=True)
df_reviews.to_sql('user_reviews', conn, if_exists='replace', index=False)
print(f"Table 'user_reviews' with {len(df_reviews)} rows.")

# Write queries to file and execute them
queries = []

# Query 1: WHERE filter using comparison / IN / BETWEEN
q1 = """
-- Query 1: WHERE filter - Apps with price between $1 and $10
SELECT App, Category, Price, Installs
FROM apps
WHERE Price BETWEEN 1.0 AND 10.0
ORDER BY Price;
"""
queries.append(q1)

# Query 2: Aggregate with GROUP BY
q2 = """
-- Query 2: Aggregate with GROUP BY - Average price and total installs per category
SELECT Category,
       COUNT(*) AS app_count,
       ROUND(AVG(Price), 2) AS avg_price,
       SUM(Installs) AS total_installs
FROM apps
GROUP BY Category
ORDER BY total_installs DESC;
"""
queries.append(q2)

# Query 3: HAVING clause
q3 = """
-- Query 3: HAVING clause - Categories with average price > $1
SELECT Category,
       COUNT(*) AS app_count,
       ROUND(AVG(Price), 2) AS avg_price
FROM apps
GROUP BY Category
HAVING AVG(Price) > 1.0
ORDER BY avg_price DESC;
"""
queries.append(q3)

# Query 4: ORDER BY with LIMIT
q4 = """
-- Query 4: ORDER BY with LIMIT - Top 10 most installed free apps
SELECT App, Category, Installs, Reviews
FROM apps
WHERE Type = 'Free'
ORDER BY Installs DESC
LIMIT 10;
"""
queries.append(q4)

# Query 5: JOIN between tables (apps and user_reviews)
q5 = """
-- Query 5: JOIN - App reviews sentiment analysis
SELECT a.App,
       a.Category,
       a.Installs,
       ROUND(AVG(ur.Sentiment_Polarity), 3) AS avg_sentiment_polarity,
       COUNT(ur.Translated_Review) AS review_count
FROM apps a
JOIN user_reviews ur ON a.App = ur.App
WHERE ur.Sentiment IS NOT NULL
GROUP BY a.App
ORDER BY avg_sentiment_polarity DESC
LIMIT 15;
"""
queries.append(q5)

# Query 6: Complex query - multiple conditions with AND/OR + subquery
q6 = """
-- Query 6: Complex query - Paid apps with high installs in specific categories
SELECT App, Category, Price, Installs, Reviews
FROM apps
WHERE Type = 'Paid'
  AND Installs > 10000
  AND Category IN ('GAME', 'FAMILY', 'TOOLS', 'PRODUCTIVITY')
ORDER BY Installs DESC
LIMIT 20;
"""
queries.append(q6)

# Write queries to file
with open('queries.sql', 'w') as f:
    f.write("-- Google Play Store Analysis SQL Queries\n")
    f.write("-- ======================================\n\n")
    for q in queries:
        f.write(q)
        f.write("\n")

print("\n--- Executing SQL Queries ---")
cursor = conn.cursor()
for i, q in enumerate(queries, 1):
    print(f"\n{'='*60}")
    print(f"Query {i}:")
    print(f"{'='*60}")
    # Extract the comment line for display
    lines = q.strip().split('\n')
    desc = [l for l in lines if l.strip().startswith('--')]
    for d in desc:
        print(f"  {d}")
    try:
        cursor.execute(q)
        results = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        print(f"  Columns: {col_names}")
        print(f"  Rows returned: {len(results)}")
        for row in results[:8]:  # Show first 8 rows
            print(f"    {row}")
        if len(results) > 8:
            print(f"    ... and {len(results)-8} more rows")
    except Exception as e:
        print(f"  ERROR: {e}")

conn.close()
print("\nSQLite database connection closed.")

# ============================================================
# 4. VISUALIZATIONS
# ============================================================
print("\n" + "=" * 70)
print("4. VISUALIZATIONS")
print("=" * 70)

# Create output directory for charts
os.makedirs('charts', exist_ok=True)

# Chart 1: Box plot - Price distribution by Type
plt.figure(figsize=(10, 6))
sns.boxplot(x='Type', y='Price', data=df_clean[df_clean['Price'] > 0])
plt.title('Box Plot: Price Distribution by App Type (Paid vs Free)')
plt.xlabel('App Type')
plt.ylabel('Price ($)')
plt.tight_layout()
plt.savefig('charts/boxplot_price_by_type.png', dpi=100)
plt.close()
print("  Chart 1 saved: charts/boxplot_price_by_type.png")

# Chart 2: Histogram - Installs distribution
plt.figure(figsize=(10, 6))
# Log scale for better visualization
df_clean['Installs_log'] = np.log1p(df_clean['Installs'])
sns.histplot(df_clean['Installs_log'], bins=50, kde=True)
plt.title('Histogram: App Installs Distribution (Log Scale)')
plt.xlabel('Log(Installs + 1)')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('charts/histogram_installs.png', dpi=100)
plt.close()
print("  Chart 2 saved: charts/histogram_installs.png")

# Chart 3: Bar chart - Top 10 categories by app count
plt.figure(figsize=(12, 6))
cat_counts = df_clean['Category'].value_counts().head(10)
sns.barplot(x=cat_counts.values, y=cat_counts.index, palette='viridis')
plt.title('Bar Chart: Top 10 Categories by Number of Apps')
plt.xlabel('Number of Apps')
plt.ylabel('Category')
plt.tight_layout()
plt.savefig('charts/barchart_top_categories.png', dpi=100)
plt.close()
print("  Chart 3 saved: charts/barchart_top_categories.png")

# Chart 4: Scatter plot - Reviews vs Installs
plt.figure(figsize=(10, 6))
sample_df = df_clean.sample(min(2000, len(df_clean)), random_state=42)
sns.scatterplot(x='Reviews', y='Installs', data=sample_df, alpha=0.5, hue='Type')
plt.title('Scatter Plot: Reviews vs Installs (Relationship between two numeric columns)')
plt.xlabel('Number of Reviews')
plt.ylabel('Number of Installs')
plt.legend(title='Type')
plt.tight_layout()
plt.savefig('charts/scatter_reviews_vs_installs.png', dpi=100)
plt.close()
print("  Chart 4 saved: charts/scatter_reviews_vs_installs.png")

# Chart 5: Grouped bar chart from pivot_table - Avg Installs by Category and Content Rating
plt.figure(figsize=(14, 7))
pivot = df_clean.pivot_table(
    values='Installs',
    index='Category',
    columns='Content Rating',
    aggfunc='mean'
)
# Take top categories by total installs
top_cats = df_clean.groupby('Category')['Installs'].sum().sort_values(ascending=False).head(10).index
pivot_top = pivot.loc[top_cats]
pivot_top.plot(kind='bar', ax=plt.gca())
plt.title('Grouped Bar Chart: Average Installs by Category and Content Rating')
plt.xlabel('Category')
plt.ylabel('Average Installs')
plt.legend(title='Content Rating', bbox_to_anchor=(1.05, 1))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('charts/groupedbar_installs_category_contentrating.png', dpi=100)
plt.close()
print("  Chart 5 saved: charts/groupedbar_installs_category_contentrating.png")

# Chart 6 (bonus): Pie chart - Free vs Paid apps
plt.figure(figsize=(8, 8))
type_counts = df_clean['Type'].value_counts()
plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%',
        startangle=90, colors=['#66b3ff', '#ff9999'])
plt.title('Pie Chart: Free vs Paid Apps Distribution')
plt.tight_layout()
plt.savefig('charts/piechart_free_vs_paid.png', dpi=100)
plt.close()
print("  Chart 6 (bonus) saved: charts/piechart_free_vs_paid.png")

print("\nAll charts saved in 'charts/' directory.")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("PROJECT SUMMARY")
print("=" * 70)
print(f"  Original dataset shape: {df.shape}")
print(f"  Cleaned dataset shape: {df_clean.shape}")
print(f"  Rows removed (duplicates + outliers): {len(df) - len(df_clean)}")
unique_dropped = list(set(cols_to_drop + (['Rating'] if 'Rating' not in df_clean.columns else [])))
print(f"  Columns dropped: {unique_dropped}")
print(f"  SQLite database: {db_path}")
print(f"  SQL queries file: queries.sql")
print(f"  Charts directory: charts/")
print(f"  Requirements file: requirements.txt")
print(f"  README file: README.md")
print("=" * 70)

print("\n✅ Analysis complete!")