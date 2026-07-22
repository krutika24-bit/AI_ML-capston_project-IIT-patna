# Google Play Store Data Analysis, Cleaning, SQL & Visualization Project

## Overview

This project performs a complete end-to-end data analysis pipeline on the **Google Play Store Apps** dataset. It covers:

- **Data Loading & Profiling** – Understanding the dataset structure, data types, and missing values.
- **Data Cleaning** – Handling missing values, duplicates, data type conversions, and outlier treatment.
- **SQLite Database & SQL Queries** – Exporting cleaned data to SQLite and executing 6 distinct analytical SQL queries.
- **Visualizations** – Generating 6 charts (box plot, histogram, bar chart, scatter plot, grouped bar chart, pie chart) using matplotlib and seaborn.

---

## Dataset

Two CSV files are used:

1. **`googleplaystore.csv`** – Main dataset with 10,841 rows and 13 columns (App, Category, Rating, Reviews, Size, Installs, Type, Price, Content Rating, Genres, Last Updated, Current Ver, Android Ver).
2. **`googleplaystore_user_reviews.csv`** – User reviews dataset with 64,295 rows and 5 columns (App, Translated_Review, Sentiment, Sentiment_Polarity, Sentiment_Subjectivity).

---

## Data Cleaning Summary

| Column | Issue | Strategy | Justification |
|--------|-------|----------|---------------|
| **Rating** | 1,474 missing values (13.6%) | **Dropped column** | >10% missing threshold; imputation would introduce significant bias. |
| **Type** | 1 missing value | **Imputed with mode** ('Free') | Only 1 missing; mode is the most representative value. |
| **Content Rating** | 1 missing value | **Imputed with mode** ('Everyone') | Only 1 missing; mode is the most representative value. |
| **Current Ver** | 8 missing values | **Imputed with mode** ('Varies with device') | <0.1% missing; mode preserves the most common value. |
| **Android Ver** | 3 missing values | **Imputed with mode** ('4.1 and up') | <0.03% missing; mode preserves the most common value. |
| **Reviews** | Stored as string (object) | **Converted to int** after stripping commas | Required for numeric analysis. |
| **Size** | Stored as string with 'M'/'k' suffixes | **Converted to float (MB)** via custom function | Required for numeric analysis. |
| **Installs** | Stored as string with commas and '+' | **Converted to int** after stripping characters | Required for numeric analysis. |
| **Price** | Stored as string with '$' prefix | **Converted to float** after stripping '$' | Required for numeric analysis. |
| **Type** | Stray values like '0' or NaN | **Cleaned to 'Free'/'Paid'** | Ensures consistent binary categorization. |
| **Duplicate Rows** | 483 duplicate rows found | **Removed via drop_duplicates()** | Ensures each app entry is unique. |
| **Reviews (Outliers)** | 1,870 outliers (18.05%) | **Capped using IQR** (upper bound: 115,962.6) | Prevents extreme values from skewing analysis. |
| **Installs (Outliers)** | 2,566 outliers (24.77%) | **Capped using IQR** (upper bound: 2,498,500) | Prevents extreme values from skewing analysis. |
| **Price (Outliers)** | 75 outliers among paid apps | **Capped using IQR** (upper bound: $10.24) | Prevents extreme prices from skewing analysis. |

**Final cleaned dataset:** 10,358 rows × 13 columns (after dropping Rating column and 483 duplicates).

---

## SQL Queries

Six SQL queries were written and executed against the SQLite database (`googleplaystore.db`):

| # | Query Type | Description | Results |
|---|------------|-------------|---------|
| 1 | **WHERE with BETWEEN** | Apps with price between $1 and $10 | 544 rows returned |
| 2 | **GROUP BY with Aggregates** | Average price and total installs per category | 34 categories; GAME has highest total installs (1.58B) |
| 3 | **HAVING clause** | Categories with average price > $1 | Only MEDICAL category (avg $1.21) |
| 4 | **ORDER BY with LIMIT** | Top 10 most installed free apps | All capped at 2,498,500 installs (IQR upper bound) |
| 5 | **JOIN** | App sentiment analysis (apps + user_reviews) | HomeWork has highest avg sentiment polarity (1.0) |
| 6 | **Complex query** | Paid apps with >10K installs in GAME/FAMILY/TOOLS/PRODUCTIVITY | 20 rows; Minecraft ($6.99) leads |

All queries are saved in **`queries.sql`**.

---

## Visualizations

Six charts were generated and saved in the `charts/` directory:

| # | Chart Type | File | Description |
|---|------------|------|-------------|
| 1 | **Box Plot** | `boxplot_price_by_type.png` | Price distribution for paid vs free apps |
| 2 | **Histogram** | `histogram_installs.png` | Distribution of app installs (log scale) |
| 3 | **Bar Chart** | `barchart_top_categories.png` | Top 10 categories by number of apps |
| 4 | **Scatter Plot** | `scatter_reviews_vs_installs.png` | Relationship between reviews and installs |
| 5 | **Grouped Bar Chart** | `groupedbar_installs_category_contentrating.png` | Average installs by category and content rating |
| 6 | **Pie Chart** | `piechart_free_vs_paid.png` | Free vs Paid app distribution |

All charts include proper titles and labeled axes.

---

## Insights

1. **Free apps dominate the market** – 92.7% of all apps on Google Play are free, with only 7.3% being paid apps. The vast majority of installs come from free apps.

2. **GAME and FAMILY categories lead in installs** – The GAME category has the highest total installs (~1.58 billion), followed by FAMILY (~1.26 billion). These two categories together account for over 40% of all app installs.

3. **MEDICAL is the only category with average price > $1** – With an average price of $1.21, the MEDICAL category has the highest average price among all 34 categories, indicating that medical apps tend to be monetized more aggressively.

4. **Reviews and Installs show a strong positive correlation** – The scatter plot reveals that apps with more reviews tend to have significantly higher installs, confirming that user engagement (reviews) is a strong proxy for app popularity.

5. **Outlier capping affected ~18-25% of numeric columns** – The IQR method identified 18% of Reviews values and 25% of Installs values as outliers, which were capped to prevent extreme values from distorting aggregate statistics.

6. **Sentiment polarity is highest for educational and productivity apps** – Apps like "HomeWork" (1.0), "Google Slides" (0.933), and "Daily Workouts" (0.8) show the highest positive sentiment, suggesting users are most satisfied with utility-focused apps.

---

## Project Files

| File | Description |
|------|-------------|
| `main.py` | Complete Python script with all analysis steps |
| `queries.sql` | 6 SQL queries for database analysis |
| `requirements.txt` | Python package dependencies |
| `README.md` | This documentation file |
| `googleplaystore.db` | SQLite database (generated by script) |
| `charts/` | Directory containing all 6 visualization PNG files |

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the analysis
python main.py
```

The script will:
- Load and profile the dataset
- Clean the data (missing values, duplicates, types, outliers)
- Create a SQLite database and execute 6 SQL queries
- Generate 6 charts in the `charts/` directory
- Print all outputs to the console

---

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- sqlite3 (built-in)


## Author
krutika Bhoi 
BCA Graduate- AIML intern 
