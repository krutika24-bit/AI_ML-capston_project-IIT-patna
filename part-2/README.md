# Predictive Modeling Pipeline - Facebook Performance Metrics

## Project Overview

This project builds a complete machine learning pipeline to predict Facebook post engagement (Total Interactions) for a renowned cosmetics brand. The pipeline includes data cleaning, feature engineering, model training, hyperparameter tuning, and evaluation.

**Problem Type:** Regression  
**Target Variable:** Total Interactions (sum of likes + comments + shares)  
**Best Model:** LinearRegression  
**Test R² Score:** 0.0014

---

## Business Problem

A cosmetics brand wants to predict how well a Facebook post will perform before publishing it. By forecasting Total Interactions, the social media team can:
- Choose the best post type (Photo, Status, Video, Link)
- Determine optimal posting time (month, weekday, hour)
- Decide whether paid promotion is worthwhile
- Maximize audience engagement and brand visibility

## Dataset Description

- **Source:** Facebook posts from a renowned cosmetics brand (2014)
- **Instances:** 500 posts
- **Features:** 19 attributes (7 pre-publication + 12 post-impact metrics)
- **Citation:** Moro et al. (2016) - Journal of Business Research

## Target

**Total Interactions** = comment + like + share

| Statistic | Value |
|-----------|-------|
| Mean | 212.12 |
| Median | 123.50 |
| Min | 0 |
| Max | 6334 |
| Std | 380.23 |

## Features

| Feature | Type | Description |
|---------|------|-------------|
| Page total likes | Numerical | Number of page fans at posting |
| Type | Nominal | Photo, Status, Video, Link |
| Category | Ordinal | 1, 2, or 3 |
| Post Month | Numerical | Month of the year (1-12) |
| Post Weekday | Numerical | Day of week (1-7) |
| Post Hour | Numerical | Hour of day (0-23) |
| Paid | Binary | Whether post was promoted |
| Page_Likes_Category | Ordinal | Binned: Small, Medium, Large |

## Preprocessing

1. **Missing Values:** Imputed comment/like/share with 0, Post Hour with median
2. **Categorical Creation:** Binned Page total likes into Small/Medium/Large
3. **Train-Test Split:** 80/20 stratified by Type (before encoding to prevent leakage)
4. **Encoding:** OneHotEncoder for Type (nominal), OrdinalEncoder for Category and Page_Likes_Category (ordinal)
5. **Scaling:** StandardScaler for numerical features (fit on training data only)

### Encoding Justification

- **OneHotEncoder:** Type is nominal (no ordering). One-hot avoids implying false ordinal relationships (e.g., Photo > Status > Video).
- **OrdinalEncoder:** Category (1,2,3) and Page_Likes_Category (Small < Medium < Large) have natural ordering, so ordinal encoding preserves this structure efficiently.

### Scaling Justification

StandardScaler centers features to mean=0 and scales to unit variance. This is critical when features have vastly different scales (Page total likes ~100,000 vs Post Hour ~12). Linear Regression and tree-based models benefit from standardized inputs for stable convergence and fair feature importance.

## Models Compared

| Model | MAE | RMSE | R² |
|-------|-----|------|----|
| Linear Regression | 154.04 | 252.74 | 0.0014 |
| Decision Tree | 192.75 | 357.34 | -0.9964 |
| Random Forest | 171.14 | 283.69 | -0.2582 |

## Evaluation Metrics

- **MAE** - Mean Absolute Error (interpretable in same units)
- **RMSE** - Root Mean Squared Error (penalizes large errors)
- **R²** - Coefficient of Determination (variance explained)

## Cross Validation Results

5-fold cross-validation on the Linear Regression model:

| Metric | Mean +/- Std |
|--------|------------|
| R² | -0.1037 +/- 0.1713 |
| MAE | 174.60 +/- 40.42 |
| RMSE | 343.04 +/- 216.37 |

## Hyperparameter Search

- **Method:** GridSearchCV with 5-fold CV
- **Parameters tuned:** ['regressor__fit_intercept']
- **Best parameters:** {'regressor__fit_intercept': True}
- **Best CV R²:** -0.1037

## Final Recommendation

**LinearRegression** is the recommended model because:
- Highest R² on test set (0.0014)
- Captures non-linear patterns in engagement data
- Robust to outliers and mixed data types
- Provides feature importance for business insights

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

See `requirements.txt` for all dependencies.

## How to Run

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Open Jupyter Notebook: `jupyter notebook Predictive_Modeling.ipynb`
4. Run all cells sequentially

## Project Structure

```
├── Predictive_Modeling.ipynb  # Main notebook
├── dataset_Facebook.csv       # Dataset
├── README.md                  # This file
├── requirements.txt           # Dependencies
```
